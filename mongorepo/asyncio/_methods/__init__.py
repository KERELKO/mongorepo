from typing import Callable
from mongorepo.asyncio._methods.arrays import (
    _pop_list_method_async,
    _update_list_field_method_async,
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


METHOD_NAME__CALLABLE: dict[str, Callable] = {
    'get': _get_method_async,
    'add': _add_method_async,
    'update': _update_method_async,
    'delete': _delete_method_async,
    'get_list': _get_list_method_async,
    'get_all': _get_all_method_async,
    'add_batch': _add_batch_method_async,
    'update_list': _update_list_field_method_async,
    'pop': _pop_list_method_async,
    'update_integer': _update_integer_field_method_async,
}

__all__ = ['METHOD_NAME__CALLABLE']
