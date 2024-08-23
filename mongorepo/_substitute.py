import inspect
from dataclasses import is_dataclass
from inspect import Parameter
from typing import Any, Callable, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo.base import DTO
from mongorepo.utils import _validate_method_annotations, replace_typevars


def _substitute_method(
    mongorepo_method: Callable,
    generic_method: Callable,
    dto: type[DTO],
    collection: Collection | AsyncIOMotorCollection,
    id_field: str | None = None,
) -> Callable:
    if id_field in mongorepo_method.__annotations__:
        mongorepo_method = mongorepo_method(dto_type=dto, collection=collection, id_field=id_field)
    else:
        mongorepo_method = mongorepo_method(dto_type=dto, collection=collection)

    is_async = inspect.iscoroutinefunction(generic_method)
    _validate_method_annotations(generic_method)

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

    new_method.__annotations__ = generic_method.__annotations__
    new_method.__name__ = generic_method.__name__
    new_method.__annotations__['return'] = dto | None

    replace_typevars(new_method, dto)

    return new_method


def _manage_params(
    mongorepo_method: Callable,
    generic_method: Callable,
    *args,
    **kwargs,
) -> dict[str, Any]:
    """Return required params for `mongorepo` method, do not pass `self` in *args or **kwargs"""
    _kwargs = {}
    gen_params = dict(inspect.signature(generic_method).parameters)
    gen_params.pop('self')
    mongo_params = dict(inspect.signature(mongorepo_method).parameters)
    mongo_params.pop('self')

    i = 0
    for param in gen_params.values():
        try:
            arg = args[i]
            i += 1
            _kwargs[param.name] = arg
        except IndexError:
            break

    for param in gen_params.values():
        if param.name not in _kwargs and param.name not in kwargs:
            raise TypeError(
                f'{generic_method.__name__}() '
                f'missing required keyword argument: \'{param.name}\''
            )
        if param.name in kwargs and param.name in _kwargs:
            raise TypeError(
                f'{generic_method.__name__}() keyword arguments repeated: {param.name}'
            )
        if param.name in _kwargs:
            continue
        _kwargs[param.name] = kwargs[param.name]

    result = {}
    extra: bool = False
    for mongo_param in mongo_params.values():
        if mongo_param.kind is Parameter.VAR_KEYWORD:
            extra = True
            break
        if isinstance(mongo_param.annotation, TypeVar) or is_dataclass(mongo_param.annotation):
            for key, value in _kwargs.items():
                if is_dataclass(value):
                    result[mongo_param.name] = value
                    _kwargs[key] = None
                    break
        else:
            for key, value in _kwargs.items():
                if isinstance(value, mongo_param.annotation):
                    result[mongo_param.name] = value
                    _kwargs[key] = None
                    break
    if extra:
        for key, value in _kwargs.items():
            if value is not None:
                result[key] = value
    return result
