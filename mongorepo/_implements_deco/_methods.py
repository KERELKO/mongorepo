import inspect
from typing import Callable, Type

from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo.base import DTO


def substitute_method(
    mongorepo_method: Callable,
    generic_method: Callable,
    dto: Type[DTO],
    collection: Collection,
    id_field: str | None = None,
) -> Callable:
    _validate_method_annotations(generic_method)

    return generic_method


def _validate_method_annotations(method: Callable) -> None:
    if 'return' not in method.__annotations__:
        raise exceptions.MongoRepoException(
            message=f'return type is not specified for "{method}" method',
        )
    params = inspect.signature(method).parameters
    if list(params)[0] != 'self':
        raise exceptions.MongoRepoException(message=f'"In {method}" self parameter is not found')
