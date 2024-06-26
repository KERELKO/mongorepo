import inspect
from typing import Any, Callable, Type, TypeVar

from pymongo.collection import Collection

from mongorepo._methods import METHOD_NAME__CALLABLE
from mongorepo import exceptions
from mongorepo.base import DTO


def substitute_method(
    mongorepo_method_name: str,
    generic_method: Callable,
    dto: Type[DTO],
    collection: Collection,
    id_field: str | None = None,
) -> Callable:

    if mongorepo_method_name not in METHOD_NAME__CALLABLE:
        raise exceptions.InvalidMethodNameException(mongorepo_method_name)
    mongorepo_method: Callable = METHOD_NAME__CALLABLE[mongorepo_method_name]
    if id_field in mongorepo_method.__annotations__:
        mongorepo_method = mongorepo_method(dto_type=dto, collection=collection, id_field=id_field)
    else:
        mongorepo_method = mongorepo_method(dto_type=dto, collection=collection)

    _validate_method_annotations(generic_method)

    has_kwargs: bool = False
    has_args: bool = False
    params_count = 0

    for param in inspect.signature(mongorepo_method).parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            has_kwargs = True
        elif param.kind == inspect.Parameter.VAR_POSITIONAL:
            has_args = True
        else:
            params_count += 1

    def func(self, *args, **kwargs) -> Any:
        required_params: list[Any] = []
        if params_count > 1:
            i = 1
            while i < params_count:

                for arg in args:
                    required_params.append(arg)
                    i += 1
                    if i == params_count:
                        break

                for key, value in kwargs.items():
                    has_param(generic_method, key)
                    required_params.append(value)
                    i += 1
                    if i == params_count:
                        break

        if has_args and has_kwargs:
            return mongorepo_method(self, *required_params, *args, **kwargs)
        elif has_args:
            return mongorepo_method(self, *required_params, *args)
        elif has_kwargs:
            return mongorepo_method(self, *required_params, **kwargs)
        return mongorepo_method(self, *required_params)

    new_method = func
    new_method.__annotations__ = generic_method.__annotations__
    new_method.__name__ = generic_method.__name__

    replace_typevar(new_method, dto)

    return new_method


def has_param(generic_method: Callable, param: Any) -> bool:
    if param not in generic_method.__annotations__:
        raise TypeError(
            f'{generic_method.__name__}() got an unexpected keyword argument \'{param}\''
        )
    return True


def _validate_method_annotations(method: Callable) -> None:
    if 'return' not in method.__annotations__:
        raise exceptions.MongoRepoException(
            message=f'return type is not specified for "{method}" method',
        )
    params = inspect.signature(method).parameters
    if list(params)[0] != 'self':
        raise exceptions.MongoRepoException(message=f'"In {method}" self parameter is not found')


def replace_typevar(func: Callable, typevar: Any) -> None:
    for param, anno in func.__annotations__.items():
        if isinstance(anno, TypeVar):
            func.__annotations__[param] = typevar
