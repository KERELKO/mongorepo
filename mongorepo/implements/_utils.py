from enum import Enum
from typing import Callable

from mongorepo import exceptions
from mongorepo._base import Dataclass, MethodAction
from mongorepo._collections import HasCollectionProvider
from mongorepo._methods.impl import AddMethod as CallableAddMethod
from mongorepo._methods.impl import \
    AppendArrayMethod as AppendArrayMethodCallable
from mongorepo._methods.impl import GetMethod as CallableGetMethod
from mongorepo._methods.impl import \
    RemoveArrayMethod as RemoveArrayMethodCallable
from mongorepo.implements.methods import (
    AddMethod,
    GetMethod,
    ListAppendMethod,
    ListRemoveMethod,
    SpecificMethod,
)


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


def implements_mapper(specific_method: SpecificMethod) -> type:
    """Map implements method to mongorepo implementation."""
    match specific_method.__class__.__name__:
        case GetMethod.__name__:
            return CallableGetMethod
        case AddMethod.__name__:
            return CallableAddMethod
        case ListAppendMethod.__name__:
            return AppendArrayMethodCallable
        case ListRemoveMethod.__name__:
            return RemoveArrayMethodCallable
    raise exceptions.MongorepoException(
        f'Cannot map specific method {specific_method.__class__} to mongorepo implementation',
    )


def initialize_callable_mongorepo_method(
    mongorepo_method: type,
    owner: HasCollectionProvider,
    dto_type: type[Dataclass],
    field_name: str | None = None,
    integer_weight: int | None = None,
    **kwargs,
) -> Callable:
    match (mcls := mongorepo_method.__name__):
        case CallableAddMethod.__name__:
            return mongorepo_method(dto_type=dto_type, owner=owner, **kwargs)
        case CallableGetMethod.__name__:
            return mongorepo_method(dto_type=dto_type, owner=owner, **kwargs)
        case AppendArrayMethodCallable.__name__:
            if not field_name:
                raise exceptions.MongorepoException(
                    f'Cannot initialize {mcls}: field_name was not provided',
                )
            return mongorepo_method(dto_type=dto_type, owner=owner, field_name=field_name, **kwargs)
        case RemoveArrayMethodCallable.__name__:
            if not field_name:
                raise exceptions.MongorepoException(
                    f'Cannot initialize {mcls}: field_name was not provided',
                )
            return mongorepo_method(dto_type=dto_type, owner=owner, field_name=field_name, **kwargs)
    raise exceptions.MongorepoException(
        f'Cannot initialize {mcls}: {mcls} is not implemented',
    )
