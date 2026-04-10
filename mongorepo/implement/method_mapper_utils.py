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
    method_mapping = {
        GetMethod: (CallableGetMethod, CallableGetMethodAsync),
        GetAllMethod: (CallableGetAllMethod, CallableGetAllMethodAsync),
        GetListMethod: (CallableGetListMethod, CallableGetListMethodAsync),
        AddBatchMethod: (CallableAddBatchMethod, CallableAddBatchMethodAsync),
        AddMethod: (CallableAddMethod, CallableAddMethodAsync),
        DeleteMethod: (CallableDeleteMethod, CallableDeleteMethodAsync),
        UpdateMethod: (CallableUpdateMethod, CallableUpdateMethodAsync),
        ListAppendMethod: (CallableAppendListMethod, CallableAppendListMethodAsync),
        ListRemoveMethod: (CallableRemoveListMethod, CallableRemoveListMethodAsync),
        ListPopMethod: (CallablePopListMethod, CallablePopListMethodAsync),
        ListItemsMethod: (CallableGetListValuesMethod, CallableGetListValuesMethodAsync),
        IncrementIntegerFieldMethod: (
            CallableIncrementIntegerFieldMethod, CallableIncrementIntegerFieldMethodAsync,
        ),
    }

    method_type = type(specific_method)

    if method_type not in method_mapping:
        raise exceptions.MongorepoException(
            f'Cannot map specific method {method_type} to mongorepo implementation',
        )

    sync_callable, async_callable = method_mapping[method_type]

    return async_callable if specific_method.is_async else sync_callable


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
