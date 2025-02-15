import inspect
from dataclasses import is_dataclass
from inspect import Parameter, _empty
from typing import Any, Callable, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import DTO, MethodAction, MethodDeps
from mongorepo._base import ParameterEnum as MongorepoParameter
from mongorepo.utils import (
    _get_defaults,
    _replace_typevars,
    _validate_method_annotations,
)

from ._utils import (
    _get_method_from_string,
    _get_mongorepo_method_callable,
    _get_validated_mongorepo_method_callable,
)
from .methods import Method, SpecificFieldMethod, SpecificMethod


def _substitute_specific_method(
    deps: MethodDeps,
    method: SpecificMethod | SpecificFieldMethod,
) -> Callable:
    is_async = inspect.iscoroutinefunction(method.source)

    if hasattr(method, 'field_name'):
        deps.custom_field_method_name = getattr(method, 'field_name')
    if hasattr(method, 'integer_weight'):
        deps.update_integer_weight = getattr(method, 'integer_weight')

    callable_mongorepo_method = _get_mongorepo_method_callable(
        method.action,
        method.mongorepo_method,
        deps,
    )

    def func(self, *args, **kwargs) -> Any:
        required_params = _manage_custom_params(
            Method(source=method.source, **method.params), *args, **kwargs,
        )
        return callable_mongorepo_method(self, **required_params)

    async def async_func(self, *args, **kwargs) -> Any:
        required_params = _manage_custom_params(
            Method(source=method.source, **method.params), *args, **kwargs,
        )
        return await callable_mongorepo_method(self, **required_params)

    if method.action == MethodAction.GET_ALL and is_async is True:
        new_method = func
    else:
        new_method = async_func if is_async else func

    new_method.__annotations__ = method.source.__annotations__
    new_method.__name__ = method.name

    _replace_typevars(new_method, deps.dto_type)

    return new_method


def _substitute_method(
    mongorepo_method_name: str,
    generic_method: Method,
    dto: type[DTO],
    collection: Collection | AsyncIOMotorCollection,
    id_field: str | None = None,
) -> Callable:

    mongorepo_method_function, mongorepo_method_type = _get_method_from_string(
        mongorepo_method_name, is_async=generic_method.is_async,
    )
    mongorepo_method = _get_validated_mongorepo_method_callable(
        mongorepo_method_name,
        mongorepo_method_type,
        mongorepo_method_function,
        dto,
        collection,
        id_field,
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

    new_method = async_func if generic_method.is_async else func

    new_method.__annotations__ = generic_method.source.__annotations__
    new_method.__name__ = generic_method.name

    _replace_typevars(new_method, dto)

    return new_method


def _manage_custom_params(
    method: Method,
    *args,
    **kwargs,
) -> dict[str, Any]:
    defaults = _get_defaults(method.source)
    result: dict[str, Any] = {}
    filters: dict[str, Any] = {}
    source_params_map: dict[str, Any] = {}
    aliases: dict[str, Any] = method.params.get(MongorepoParameter.FILTER_ALIAS, {})  # type: ignore
    i = 0

    # Iterate over all names of the method's arguments
    for source_param in method.get_source_params().keys():

        # Parameter was passed as positional argument
        if len(args) > i:
            source_params_map[source_param] = args[i]
            i += 1
            continue

        # Parameter was passed as keyword argument ?
        elif source_param in kwargs:
            source_params_map[source_param] = kwargs[source_param]

        # If parameter was not passed check for defaults
        elif defaults.get(source_param, None):
            source_params_map[source_param] = defaults[source_param]

        # Missing parameter
        else:
            raise exceptions.MongoRepoException(
                message=f'Cannot find value for {source_param} parameter. '
                f'{method.name}() parameters: {method.params}',
            )

    for key, value in source_params_map.items():
        if method.params.get(key, None) == MongorepoParameter.FILTER:
            filters[key] = value
        elif (dto_field := aliases.get(key, None)) is not None:
            filters[dto_field] = value
        else:
            result[method.params[key]] = value

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
