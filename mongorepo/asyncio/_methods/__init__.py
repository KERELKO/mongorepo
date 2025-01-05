from typing import Callable

from mongorepo._base import MethodAction
from mongorepo.asyncio._methods.arrays import (
    _get_list_of_field_values_method_async,
    _pop_list_method_async,
    _update_list_field_method_async,
)
from mongorepo.asyncio._methods.crud import (
    _add_batch_method_async,
    _add_method_async,
    _delete_method_async,
    _get_all_method_async,
    _get_list_method_async,
    _get_method_async,
    _update_method_async,
)
from mongorepo.asyncio._methods.integer import (
    _update_integer_field_method_async,
)

# List methods, all starts with `__`
LIST_METHODS_ASYNC: dict[str, Callable] = {
    MethodAction.LIST_FIELD_VALUES: _get_list_of_field_values_method_async,
    MethodAction.LIST_POP: _pop_list_method_async,
    MethodAction.LIST_APPEND: _update_list_field_method_async,
    MethodAction.LIST_REMOVE: _update_list_field_method_async,
}

# Integer methods, all ends with `__`
INTEGER_METHODS_ASYNC: dict[str, Callable] = {
    MethodAction.INTEGER_INCREMENT: _update_integer_field_method_async,
    MethodAction.INTEGER_DECREMENT: _update_integer_field_method_async,
}

# CRUD methods
CRUD_METHODS_ASYNC: dict[str, Callable] = {
    MethodAction.GET: _get_method_async,
    MethodAction.ADD: _add_method_async,
    MethodAction.UPDATE: _update_method_async,
    MethodAction.DELETE: _delete_method_async,
    MethodAction.GET_LIST: _get_list_method_async,
    MethodAction.GET_ALL: _get_all_method_async,
    MethodAction.ADD_BATCH: _add_batch_method_async,
}

__all__ = ['LIST_METHODS_ASYNC', 'CRUD_METHODS_ASYNC', 'INTEGER_METHODS_ASYNC']
