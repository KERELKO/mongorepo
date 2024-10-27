import inspect
from dataclasses import is_dataclass
from enum import Enum
from inspect import Parameter, _empty
from typing import Any, Callable, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import DTO, Method, _FiltersParameter
from mongorepo._methods import CRUD_METHODS, INTEGER_METHODS, LIST_METHODS
from mongorepo.asyncio._methods import (
    CRUD_METHODS_ASYNC,
    INTEGER_METHODS_ASYNC,
    LIST_METHODS_ASYNC,
)
from mongorepo.utils import (
    _check_valid_field_type,
    _get_defaults,
    _replace_typevars,
    _validate_method_annotations,
)


class _MethodType(Enum):
    CRUD = 1
    LIST = 2
    INTEGER = 3


VALID_ACTIONS_FOR_INTEGER_METHODS: tuple[str, ...] = ('incr', 'decr')
VALID_ACTIONS_FOR_ARRAY_METHODS: tuple[str, ...] = ('pop', 'list', 'append', 'remove')


def _substitute_method(
    mongorepo_method_name: str,
    generic_method: Method,
    dto: type[DTO],
    collection: Collection | AsyncIOMotorCollection,
    id_field: str | None = None,
) -> Callable:
    is_async = inspect.iscoroutinefunction(generic_method)

    mongorepo_method = _get_mongorepo_method_callable(
        mongorepo_method_name, generic_method, dto, collection, id_field,
    )

    _validate_method_annotations(generic_method.source)

    def func(self, *args, **kwargs) -> Any:
        required_params = _manage_params(
            mongorepo_method, generic_method, *args, **kwargs,
        )
        return mongorepo_method(self, **required_params)

    async def async_func(self, *args, **kwargs) -> Any:
        required_params = _manage_params(
            mongorepo_method, generic_method, *args, **kwargs,
        )
        return await mongorepo_method(self, **required_params)

    new_method = async_func if is_async else func

    new_method.__annotations__ = generic_method.source.__annotations__
    new_method.__name__ = generic_method.name

    _replace_typevars(new_method, dto)

    return new_method


def _manage_custom_params(
    generic_method: Method,
    *args,
    **kwargs,
) -> dict[str, Any]:
    defaults = _get_defaults(generic_method.source)
    result: dict[str, Any] = {}
    gen_map = {}
    filters: dict[str, Any] = {}
    i = 0
    for gen_param in generic_method.get_source_params().keys():
        if len(args) > i:
            gen_map[gen_param] = args[i]
            i += 1
            continue
        elif gen_param in kwargs:
            gen_map[gen_param] = kwargs[gen_param]
        elif defaults.get(gen_param, None):
            gen_map[gen_param] = defaults[gen_param]
        else:
            raise exceptions.MongoRepoException(
                message=f'Cannot find value for {gen_param} parameter. '
                f'{generic_method.name}() parameters: {generic_method.params}',
            )

    for key, value in gen_map.items():
        if generic_method.params[key] == _FiltersParameter.FILTER.value:
            filters[key] = value
        else:
            result[generic_method.params[key]] = value

    result.update(filters)
    return result


def _manage_params(
    mongorepo_method: Callable,
    generic_method: Method,
    *args,
    **kwargs,
) -> dict[str, Any]:
    """Return required params for `mongorepo` method, do not pass `self` in
    *args or **kwargs."""

    if generic_method.params:
        return _manage_custom_params(
            generic_method, *args, **kwargs,
        )

    params: dict[str, Any] = {}
    result: dict[str, Any] = {}

    # control for **kwargs in source method
    extra: bool = False

    mongo_params = dict(inspect.signature(mongorepo_method).parameters)
    mongo_params.pop('self')

    gen_params = dict(generic_method.signature.parameters)
    gen_params.pop('self')

    i = 0
    # Looping over *args and unite them with generic method parameters
    for param in gen_params.values():
        try:
            arg = args[i]
        except IndexError:
            break
        i += 1
        params[param.name] = arg

    # Looping over **kwargs and unite them with generic method parameters
    for param in gen_params.values():
        if param.name in kwargs and param.name in params:
            raise TypeError(
                f'{generic_method.name}() keyword arguments repeated: {param.name}',
            )

        if param.default != _empty and not kwargs.get(param.name, None):
            params[param.name] = param.default

        if param.name in params:
            continue

        if param.name not in params and param.name not in kwargs:
            raise TypeError(
                f'{generic_method.name}() '
                f'missing required keyword argument: \'{param.name}\'',
            )
        params[param.name] = kwargs[param.name]

    # Unite generic method arguments to mongorepo arguments of the method
    for mongo_param in mongo_params.values():
        if mongo_param.kind is Parameter.VAR_KEYWORD:
            extra = True
            break

        # Try to find DTO type and unite with parameter with DTO annotation
        if isinstance(mongo_param.annotation, TypeVar) or is_dataclass(mongo_param.annotation):
            for key, value in params.items():
                if is_dataclass(value):
                    result[mongo_param.name] = value
                    params[key] = None
                    break
        else:
            for key, value in params.items():
                if mongo_param.annotation == Any or isinstance(value, mongo_param.annotation):
                    result[mongo_param.name] = value
                    params[key] = None
                    break

    # Looping over mongorepo **kwargs if they not absent
    if extra:
        for key, value in params.items():
            if value is not None:
                result[key] = value
    return result


def _get_method_from_string(
    method_name: str, is_async: bool = False,
) -> tuple[Callable, _MethodType]:
    """Tries to get right `mongorepo` method according to `method_name`

    returns tuple where first element is a method, and the second its type

    ### Example:

    ```
    method = get_method_from_string(method_name='messages__list', is_async=True)
    ```

    """
    if is_async:
        if method_name in CRUD_METHODS_ASYNC and is_async:
            return (CRUD_METHODS_ASYNC[method_name], _MethodType.CRUD)

        for key, value in LIST_METHODS_ASYNC.items():
            if method_name.endswith(key):
                return (value, _MethodType.LIST)

        for key, value in INTEGER_METHODS_ASYNC.items():
            if method_name.startswith(key):
                return (value, _MethodType.INTEGER)
    else:
        if method_name in CRUD_METHODS:
            return (CRUD_METHODS[method_name], _MethodType.CRUD)

        for key, value in LIST_METHODS.items():
            if method_name.endswith(key):
                return (value, _MethodType.LIST)

        for key, value in INTEGER_METHODS.items():
            if method_name.startswith(key):
                return (value, _MethodType.INTEGER)

    msg = (
        f'Mongorepo does not have method with this action: {method_name}\n'
        f'Use valid prefix or suffix to specify correct method that you want to use\n'
        f'For example: "records__pop" where "records" is the name of list field and '
        '"__pop" action to pop the last element in the list'
    )

    raise exceptions.InvalidMethodNameException(
        method_name=method_name,
        message=msg,
    )


def _get_mongorepo_method_callable(
    mongorepo_method_name: str,
    generic_method: Method,
    dto: type[DTO],
    collection: Collection | AsyncIOMotorCollection,
    id_field: str | None = None,
) -> Callable:
    is_async = inspect.iscoroutinefunction(generic_method.source)

    mongorepo_method, mongorepo_method_type = _get_method_from_string(
        mongorepo_method_name, is_async=is_async,
    )
    if mongorepo_method_type is _MethodType.CRUD:
        if id_field in mongorepo_method.__annotations__:
            mongorepo_method = mongorepo_method(
                dto_type=dto, collection=collection, id_field=id_field,
            )
        else:
            mongorepo_method = mongorepo_method(dto_type=dto, collection=collection)

    elif mongorepo_method_type is _MethodType.INTEGER:
        action, field_name = (d := mongorepo_method_name.split('__'))[0], d[-1]
        _check_valid_field_type(field_name, dto, int)
        if action not in VALID_ACTIONS_FOR_INTEGER_METHODS:
            raise exceptions.MongoRepoException(
                message=f'Invalid action for {mongorepo_method_name}(): '
                f'{action}\n valid: {VALID_ACTIONS_FOR_INTEGER_METHODS}',
            )
        mongorepo_method = mongorepo_method(
            dto_type=dto,
            collection=collection,
            field_name=field_name,
            _weight=1 if action == 'incr' else -1,
        )

    elif mongorepo_method_type is _MethodType.LIST:
        action, field_name = (d := mongorepo_method_name.split('__'))[-1], d[0]
        _check_valid_field_type(field_name, dto, list)
        if action not in VALID_ACTIONS_FOR_ARRAY_METHODS:
            raise exceptions.MongoRepoException(
                message=f'Invalid action for {mongorepo_method_name}(): '
                f'{action}\n valid: {VALID_ACTIONS_FOR_ARRAY_METHODS}',
            )
        if 'command' in mongorepo_method.__annotations__:
            mongorepo_method = mongorepo_method(
                dto_type=dto,
                collection=collection,
                field_name=field_name,
                command='$push' if action == 'append' else '$pull',
            )
        else:
            mongorepo_method = mongorepo_method(
                dto_type=dto,
                collection=collection,
                field_name=field_name,
            )
    return mongorepo_method
