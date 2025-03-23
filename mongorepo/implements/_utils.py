from typing import Callable

from mongorepo import exceptions
from mongorepo._base import Dataclass
from mongorepo._collections import HasCollectionProvider
from mongorepo._methods.impl import AddBatchMethod as CallableAddBatchMethod
from mongorepo._methods.impl import AddMethod as CallableAddMethod
from mongorepo._methods.impl import \
    AppendListMethod as CallableAppendListMethod
from mongorepo._methods.impl import DeleteMethod as CallableDeleteMethod
from mongorepo._methods.impl import GetAllMethod as CallableGetAllMethod
from mongorepo._methods.impl import GetListMethod as CallableGetListMethod
from mongorepo._methods.impl import \
    GetListValuesMethod as CallableGetListValuesMethod
from mongorepo._methods.impl import GetMethod as CallableGetMethod
from mongorepo._methods.impl import \
    IncrementIntegerFieldMethod as CallableIncrementIntegerFieldMethod
from mongorepo._methods.impl import PopListMethod as CallablePopListMethod
from mongorepo._methods.impl import \
    RemoveListMethod as CallableRemoveListMethod
from mongorepo._methods.impl import UpdateMethod as CallableUpdateMethod
from mongorepo.implements.methods import (
    AddBatchMethod,
    AddMethod,
    DeleteMethod,
    GetAllMethod,
    GetListMethod,
    GetMethod,
    IncrementIntegerFieldMethod,
    ListAppendMethod,
    ListGetFieldValuesMethod,
    ListPopMethod,
    ListRemoveMethod,
    SpecificMethod,
    UpdateMethod,
)


def implements_mapper(specific_method: SpecificMethod) -> type:
    """Map implements method to mongorepo implementation."""
    match specific_method.__class__.__name__:
        case GetMethod.__name__:
            return CallableGetMethod
        case GetAllMethod.__name__:
            return CallableGetAllMethod
        case GetListMethod.__name__:
            return CallableGetListMethod
        case AddBatchMethod.__name__:
            return CallableAddBatchMethod
        case AddMethod.__name__:
            return CallableAddMethod
        case DeleteMethod.__name__:
            return CallableDeleteMethod
        case UpdateMethod.__name__:
            return CallableUpdateMethod

        case ListAppendMethod.__name__:
            return CallableAppendListMethod
        case ListRemoveMethod.__name__:
            return CallableRemoveListMethod
        case ListPopMethod.__name__:
            return CallablePopListMethod
        case ListGetFieldValuesMethod.__name__:
            return CallableGetListValuesMethod

        case IncrementIntegerFieldMethod.__name__:
            return CallableIncrementIntegerFieldMethod

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
        case CallableGetListMethod.__name__:
            return mongorepo_method(dto_type, owner=owner, **kwargs)
        case CallableAddBatchMethod.__name__:
            return mongorepo_method(dto_type=dto_type, owner=owner, **kwargs)
        case CallableGetAllMethod.__name__:
            return mongorepo_method(dto_type=dto_type, owner=owner, **kwargs)
        case CallableUpdateMethod.__name__:
            return mongorepo_method(dto_type=dto_type, owner=owner, **kwargs)
        case CallableDeleteMethod.__name__:
            return mongorepo_method(dto_type=dto_type, owner=owner, **kwargs)

        case CallablePopListMethod.__name__:
            if not field_name:
                raise exceptions.MongorepoException(
                    f'Cannot initialize {mcls}: field_name was not provided',
                )
            return mongorepo_method(dto_type=dto_type, owner=owner, field_name=field_name, **kwargs)
        case CallableAppendListMethod.__name__:
            if not field_name:
                raise exceptions.MongorepoException(
                    f'Cannot initialize {mcls}: field_name was not provided',
                )
            return mongorepo_method(dto_type=dto_type, owner=owner, field_name=field_name, **kwargs)
        case CallableRemoveListMethod.__name__:
            if not field_name:
                raise exceptions.MongorepoException(
                    f'Cannot initialize {mcls}: field_name was not provided',
                )
            return mongorepo_method(dto_type=dto_type, owner=owner, field_name=field_name, **kwargs)
        case CallableGetListValuesMethod.__name__:
            if not field_name:
                raise exceptions.MongorepoException(
                    f'Cannot initialize {mcls}: field_name was not provided',
                )
            return mongorepo_method(dto_type=dto_type, owner=owner, field_name=field_name, **kwargs)

        case CallableIncrementIntegerFieldMethod.__name__:
            if not field_name or not integer_weight:
                raise exceptions.MongorepoException(
                    f'Cannot initialize {mcls}: field_name or weight was not provided: '
                    f'{field_name=}, {integer_weight=}',
                )
            return mongorepo_method(dto_type, owner, field_name, weight=integer_weight, **kwargs)

    raise exceptions.MongorepoException(
        f'Cannot initialize {mcls}: {mcls} is not implemented',
    )
