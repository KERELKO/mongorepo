from enum import Enum
from typing import Callable

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import DTO, MethodAction, MethodDeps
from mongorepo._methods import CRUD_METHODS, INTEGER_METHODS, LIST_METHODS
from mongorepo.asyncio._methods import (
    CRUD_METHODS_ASYNC,
    INTEGER_METHODS_ASYNC,
    LIST_METHODS_ASYNC,
)
from mongorepo.utils import _check_valid_field_type


class MethodType(Enum):
    CRUD = 1
    LIST = 2
    INTEGER = 3

    @staticmethod
    def from_action(action: MethodAction) -> 'MethodType':
        if action.value.startswith('__'):
            return MethodType.LIST
        elif action.value.endswith('__'):
            return MethodType.INTEGER
        elif action in MethodAction:
            return MethodType.CRUD
        raise exceptions.InvalidActionException(
            action=action, valid_actions=[a.value for a in MethodAction],
        )


def _get_method_from_string(
    method_name: str, is_async: bool = False,
) -> tuple[Callable, MethodType]:
    """Tries to get right `mongorepo` method according to `method_name`

    returns tuple where first element is a method, and the second its type

    ### Example:

    ```
    method = get_method_from_string(method_name='messages__list', is_async=True)
    ```

    """
    if is_async:
        if method_name in CRUD_METHODS_ASYNC:
            return (CRUD_METHODS_ASYNC[method_name], MethodType.CRUD)

        for key, value in LIST_METHODS_ASYNC.items():
            if method_name.endswith(key):
                return (value, MethodType.LIST)

        for key, value in INTEGER_METHODS_ASYNC.items():
            if method_name.startswith(key):
                return (value, MethodType.INTEGER)
    else:
        if method_name in CRUD_METHODS:
            return (CRUD_METHODS[method_name], MethodType.CRUD)

        for key, value in LIST_METHODS.items():
            if method_name.endswith(key):
                return (value, MethodType.LIST)

        for key, value in INTEGER_METHODS.items():
            if method_name.startswith(key):
                return (value, MethodType.INTEGER)

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


# TODO: reduce repeated parts with _get_mongorepo_method_callable()
def _get_validated_mongorepo_method_callable(
    mongorepo_method_name: str,
    mongorepo_method_type: MethodType,
    mongorepo_method: Callable,
    dto: type[DTO],
    collection: Collection | AsyncIOMotorCollection,
    id_field: str | None = None,
) -> Callable:
    """Tries to parse `mongorepo_method_name` to get method action.

    After parsing passes required parameters to the mongorepo method
    decorator to get callable method

    """
    if mongorepo_method_type is MethodType.CRUD:
        if id_field in mongorepo_method.__annotations__:
            mongorepo_method = mongorepo_method(
                dto_type=dto, collection=collection, id_field=id_field,
            )
        else:
            mongorepo_method = mongorepo_method(dto_type=dto, collection=collection)

    elif mongorepo_method_type is MethodType.INTEGER:
        action, field_name = (d := mongorepo_method_name.split('__'))[0] + '__', d[-1]
        _check_valid_field_type(field_name, dto, int)
        if action not in MethodAction:
            raise exceptions.InvalidActionException(
                action=action,
                valid_actions=(valid_actions := [act.value for act in MethodAction]),
                message=f'Invalid action for {mongorepo_method_name}(): '
                f'{action}\n valid: {valid_actions}',
            )
        mongorepo_method = mongorepo_method(
            dto_type=dto,
            collection=collection,
            field_name=field_name,
            _weight=1 if action == MethodAction.INTEGER_INCREMENT else -1,
        )

    elif mongorepo_method_type is MethodType.LIST:
        action, field_name = '__' + (d := mongorepo_method_name.split('__'))[-1], d[0]
        _check_valid_field_type(field_name, dto, list)
        if action not in MethodAction:
            raise exceptions.InvalidActionException(
                action=action,
                valid_actions=(valid_actions := [act.value for act in MethodAction]),
                message=f'Invalid action for {mongorepo_method_name}(): '
                f'{action}\n valid: {valid_actions}',
            )
        if 'command' in mongorepo_method.__annotations__:
            mongorepo_method = mongorepo_method(
                dto_type=dto,
                collection=collection,
                field_name=field_name,
                command='$push' if action == MethodAction.LIST_APPEND else '$pull',
            )
        else:
            mongorepo_method = mongorepo_method(
                dto_type=dto,
                collection=collection,
                field_name=field_name,
            )
    return mongorepo_method


def _get_mongorepo_method_callable(
    action: MethodAction,
    mongorepo_method: Callable,
    deps: MethodDeps,
) -> Callable:
    """Tries to parse `mongorepo_method_name` to get method action.

    After parsing passes required parameters to the mongorepo method
    decorator to get callable method

    """
    mongorepo_method_type = MethodType.from_action(action)

    match mongorepo_method_type:
        case MethodType.CRUD:
            if deps.id_field in mongorepo_method.__annotations__:
                mongorepo_method = mongorepo_method(
                    dto_type=deps.dto_type, collection=deps.collection, id_field=deps.id_field,
                )
            else:
                mongorepo_method = mongorepo_method(
                    dto_type=deps.dto_type, collection=deps.collection,
                )
        case MethodType.INTEGER:
            mongorepo_method = mongorepo_method(
                dto_type=deps.dto_type,
                collection=deps.collection,
                field_name=deps.custom_field_method_name,
                _weight=1 if action == MethodAction.INTEGER_INCREMENT else -1,
            )
        case MethodType.LIST:
            if 'command' in mongorepo_method.__annotations__:
                mongorepo_method = mongorepo_method(
                    dto_type=deps.dto_type,
                    collection=deps.collection,
                    field_name=deps.custom_field_method_name,
                    command='$push' if action == MethodAction.LIST_APPEND else '$pull',
                )
            else:
                mongorepo_method = mongorepo_method(
                    dto_type=deps.dto_type,
                    collection=deps.collection,
                    field_name=deps.custom_field_method_name,
                )
    return mongorepo_method
