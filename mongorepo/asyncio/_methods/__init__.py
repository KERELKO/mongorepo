from typing import Callable

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
    '__list': _get_list_of_field_values_method_async,
    '__pop': _pop_list_method_async,
    '__append': _update_list_field_method_async,
    '__remove': _update_list_field_method_async,
}

# Integer methods, all ends with `__`
INTEGER_METHODS_ASYNC: dict[str, Callable] = {
    'incr__': _update_integer_field_method_async,
    'decr__': _update_integer_field_method_async,
}

# CRUD methods
CRUD_METHODS_ASYNC: dict[str, Callable] = {
    'get': _get_method_async,
    'add': _add_method_async,
    'update': _update_method_async,
    'delete': _delete_method_async,
    'get_list': _get_list_method_async,
    'get_all': _get_all_method_async,
    'add_batch': _add_batch_method_async,
}

__all__ = ['LIST_METHODS_ASYNC', 'CRUD_METHODS_ASYNC', 'INTEGER_METHODS_ASYNC']
