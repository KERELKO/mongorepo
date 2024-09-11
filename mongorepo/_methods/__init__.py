from typing import Callable

from mongorepo._methods.arrays import (
    _pop_list_method,
    _update_list_field_method,
    _get_list_of_field_values_method,
)
from mongorepo._methods.crud import (
    _add_method,
    _delete_method,
    _get_all_method,
    _get_list_method,
    _get_method,
    _add_batch_method,
    _update_method,
)
from mongorepo._methods.integer import _update_integer_field_method


METHOD_NAME__CALLABLE: dict[str, Callable] = {
    # Standard methods
    'get': _get_method,
    'add': _add_method,
    'update': _update_method,
    'delete': _delete_method,
    'get_list': _get_list_method,
    'get_all': _get_all_method,
    'add_batch': _add_batch_method,

    # List methods
    '__list': _get_list_of_field_values_method,
    '__pop': _pop_list_method,
    '__append': _update_list_field_method,
    '__remove': _update_list_field_method,

    # Integer methods
    'incr__': _update_integer_field_method,
    'decr__': _update_integer_field_method,
}

__all__ = ['METHOD_NAME__CALLABLE']
