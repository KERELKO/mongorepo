import inspect
from enum import Enum
from typing import Callable

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import DTO
from mongorepo._methods import CRUD_METHODS, INTEGER_METHODS, LIST_METHODS
from mongorepo.asyncio._methods import (
    CRUD_METHODS_ASYNC,
    INTEGER_METHODS_ASYNC,
    LIST_METHODS_ASYNC,
)
from mongorepo.utils import _check_valid_field_type

from .methods import Method


class _MethodType(Enum):
    CRUD = 1
    LIST = 2
    INTEGER = 3


VALID_ACTIONS_FOR_INTEGER_METHODS: tuple[str, ...] = ('incr', 'decr')
VALID_ACTIONS_FOR_ARRAY_METHODS: tuple[str, ...] = ('pop', 'list', 'append', 'remove')


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
        if method_name in CRUD_METHODS_ASYNC:
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
