from typing import Callable

from mongorepo._base import MethodAction
from mongorepo._methods.arrays import (
    _get_list_of_field_values_method,
    _pop_list_method,
    _update_list_field_method,
)
from mongorepo._methods.crud import (
    _add_batch_method,
    _add_method,
    _delete_method,
    _get_all_method,
    _get_list_method,
    _get_method,
    _update_method,
)
from mongorepo._methods.integer import _update_integer_field_method

# List methods, all starts with `__`
LIST_METHODS: dict[str, Callable] = {
    MethodAction.LIST_FIELD_VALUES: _get_list_of_field_values_method,
    MethodAction.LIST_POP: _pop_list_method,
    MethodAction.LIST_APPEND: _update_list_field_method,
    MethodAction.LIST_REMOVE: _update_list_field_method,
}

# Integer methods, all ends with `__`
INTEGER_METHODS: dict[str, Callable] = {
    MethodAction.INTEGER_INCREMENT: _update_integer_field_method,
    MethodAction.INTEGER_DECREMENT: _update_integer_field_method,
}

# CRUD methods
CRUD_METHODS: dict[str, Callable] = {
    MethodAction.GET: _get_method,
    MethodAction.ADD: _add_method,
    MethodAction.UPDATE: _update_method,
    MethodAction.DELETE: _delete_method,
    MethodAction.GET_LIST: _get_list_method,
    MethodAction.GET_ALL: _get_all_method,
    MethodAction.ADD_BATCH: _add_batch_method,
}

__all__ = ['LIST_METHODS', 'CRUD_METHODS', 'INTEGER_METHODS']
