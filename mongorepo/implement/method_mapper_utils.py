from typing import Callable

from mongorepo import exceptions
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
from mongorepo._methods.impl_async import \
    AddBatchMethodAsync as CallableAddBatchMethodAsync
from mongorepo._methods.impl_async import \
    AddMethodAsync as CallableAddMethodAsync
from mongorepo._methods.impl_async import \
    AppendListMethodAsync as CallableAppendListMethodAsync
from mongorepo._methods.impl_async import \
    DeleteMethodAsync as CallableDeleteMethodAsync
from mongorepo._methods.impl_async import \
    GetAllMethodAsync as CallableGetAllMethodAsync
from mongorepo._methods.impl_async import \
    GetListMethodAsync as CallableGetListMethodAsync
from mongorepo._methods.impl_async import \
    GetListValuesMethodAsync as CallableGetListValuesMethodAsync
from mongorepo._methods.impl_async import \
    GetMethodAsync as CallableGetMethodAsync
from mongorepo._methods.impl_async import \
    IncrementIntegerFieldMethodAsync as \
    CallableIncrementIntegerFieldMethodAsync
from mongorepo._methods.impl_async import \
    PopListMethodAsync as CallablePopListMethodAsync
from mongorepo._methods.impl_async import \
    RemoveListMethodAsync as CallableRemoveListMethodAsync
from mongorepo._methods.impl_async import \
    UpdateMethodAsync as CallableUpdateMethodAsync
from mongorepo.implement.methods import (
    AddBatchMethod,
    AddMethod,
    DeleteMethod,
    GetAllMethod,
    GetListMethod,
    GetMethod,
    IncrementIntegerFieldMethod,
    ListAppendMethod,
    ListItemsMethod,
    ListPopMethod,
    ListRemoveMethod,
    SpecificMethod,
    UpdateMethod,
)
from mongorepo.types import Field


def implement_mapper(specific_method: SpecificMethod) -> type:
    """Map implement method to mongorepo implementation."""
    s = specific_method
    match specific_method.__class__.__name__:
        case GetMethod.__name__:
            return CallableGetMethodAsync if s.is_async else CallableGetMethod
        case GetAllMethod.__name__:
            return CallableGetAllMethodAsync if s.is_async else CallableGetAllMethod
        case GetListMethod.__name__:
            return CallableGetListMethodAsync if s.is_async else CallableGetListMethod
        case AddBatchMethod.__name__:
            return CallableAddBatchMethodAsync if s.is_async else CallableAddBatchMethod
        case AddMethod.__name__:
            return CallableAddMethodAsync if s.is_async else CallableAddMethod
        case DeleteMethod.__name__:
            return CallableDeleteMethodAsync if s.is_async else CallableDeleteMethod
        case UpdateMethod.__name__:
            return CallableUpdateMethodAsync if s.is_async else CallableUpdateMethod

        case ListAppendMethod.__name__:
            return CallableAppendListMethodAsync if s.is_async else CallableAppendListMethod
        case ListRemoveMethod.__name__:
            return CallableRemoveListMethodAsync if s.is_async else CallableRemoveListMethod
        case ListPopMethod.__name__:
            return CallablePopListMethodAsync if s.is_async else CallablePopListMethod
        case ListItemsMethod.__name__:
            return CallableGetListValuesMethodAsync if s.is_async else CallableGetListValuesMethod

        case IncrementIntegerFieldMethod.__name__:
            if s.is_async:
                return CallableIncrementIntegerFieldMethodAsync
            else:
                return CallableIncrementIntegerFieldMethod

    raise exceptions.MongorepoException(
        f'Cannot map specific method {specific_method.__class__} to mongorepo implementation',
    )


def initialize_callable_mongorepo_method(
    mongorepo_method: type,
    owner: type,
    entity_type: type,
    target_field: Field | None = None,
    integer_weight: int | None = None,
    **kwargs,
) -> Callable:

    standard_methods = {
        CallableAddMethod, CallableAddMethodAsync,
        CallableGetMethod, CallableGetMethodAsync,
        CallableGetListMethod, CallableGetListMethodAsync,
        CallableAddBatchMethod, CallableAddBatchMethodAsync,
        CallableGetAllMethod, CallableGetAllMethodAsync,
        CallableUpdateMethod, CallableUpdateMethodAsync,
        CallableDeleteMethod, CallableDeleteMethodAsync,
    }

    field_methods = {
        CallablePopListMethod, CallablePopListMethodAsync,
        CallableAppendListMethod, CallableAppendListMethodAsync,
        CallableRemoveListMethod, CallableRemoveListMethodAsync,
        CallableGetListValuesMethod, CallableGetListValuesMethodAsync,
    }

    increment_methods = {
        CallableIncrementIntegerFieldMethod, CallableIncrementIntegerFieldMethodAsync,
    }

    mcls = mongorepo_method.__name__

    if mongorepo_method in standard_methods:
        return mongorepo_method(entity_type=entity_type, owner=owner, **kwargs)

    if mongorepo_method in field_methods:
        if not target_field:
            raise exceptions.MongorepoException(
                f'Cannot initialize {mcls}: target_field was not provided',
            )
        return mongorepo_method(
            entity_type=entity_type, owner=owner, target_field=target_field, **kwargs,
        )

    if mongorepo_method in increment_methods:
        if not target_field or not integer_weight:
            raise exceptions.MongorepoException(
                f'Cannot initialize {mcls}: target_field or weight was not provided: '
                f'{target_field=}, {integer_weight=}',
            )
        return mongorepo_method(
            entity_type=entity_type,
            owner=owner,
            target_field=target_field,
            weight=integer_weight,
            **kwargs,
        )

    raise exceptions.MongorepoException(f'Cannot initialize {mcls}: {mcls} is not implemented')
