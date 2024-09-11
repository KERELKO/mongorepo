from typing import Callable
from mongorepo.asyncio._methods.arrays import (
    _pop_list_method_async,
    _update_list_field_method_async,
    _get_list_of_field_values_method_async,
)
from mongorepo.asyncio._methods.crud import (
    _add_method_async,
    _delete_method_async,
    _get_all_method_async,
    _get_list_method_async,
    _get_method_async,
    _add_batch_method_async,
    _update_method_async,
)
from mongorepo.asyncio._methods.integer import _update_integer_field_method_async


METHOD_NAME__CALLABLE_ASYNC: dict[str, Callable] = {
    # Standard methods
    'get': _get_method_async,
    'add': _add_method_async,
    'update': _update_method_async,
    'delete': _delete_method_async,
    'get_list': _get_list_method_async,
    'get_all': _get_all_method_async,
    'add_batch': _add_batch_method_async,

    # List methods
    '__list': _get_list_of_field_values_method_async,
    '__pop': _pop_list_method_async,
    '__append': _update_list_field_method_async,
    '__remove': _update_list_field_method_async,

    # Integer methods
    'incr__': _update_integer_field_method_async,
    'decr__': _update_integer_field_method_async,
}

__all__ = ['METHOD_NAME__CALLABLE_ASYNC']
