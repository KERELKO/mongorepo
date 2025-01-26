import asyncio

from mongorepo._base import Access
from mongorepo._setters import (
    _set_array_fields_methods,
    _set_crud_methods,
    _set_integer_fields_methods,
)
from mongorepo.asyncio.utils import _create_index_async
from mongorepo.utils import (
    _create_index,
    _get_meta_attributes,
    _set__methods__,
)


def _handle_mongo_repository(
    cls,
    add: bool,
    get: bool,
    add_batch: bool,
    get_all: bool,
    update: bool,
    delete: bool,
    get_list: bool,
    __methods__: bool,
    integer_fields: list[str] | None,
    array_fields: list[str] | None,
    method_access: Access | None,
) -> type:
    """Calls for functions that set different methods and attributes to the
    class."""
    attributes = _get_meta_attributes(cls, raise_exceptions=False)
    collection = attributes['collection']
    index = attributes['index']

    _set_crud_methods(
        cls,
        add=add,
        get=get,
        get_all=get_all,
        get_list=get_list,
        update=update,
        delete=delete,
        add_batch=add_batch,
        method_access=method_access,
    )

    if index is not None:
        _create_index(index=index, collection=collection)

    if integer_fields is not None:
        _set_integer_fields_methods(cls, integer_fields=integer_fields, method_access=method_access)

    if array_fields is not None:
        _set_array_fields_methods(cls, array_fields=array_fields, method_access=method_access)

    if __methods__:
        _set__methods__(cls)
    return cls


def _handle_async_mongo_repository(
    cls,
    add: bool,
    add_batch: bool,
    get: bool,
    get_all: bool,
    get_list: bool,
    update: bool,
    delete: bool,
    __methods__: bool,
    integer_fields: list[str] | None,
    array_fields: list[str] | None,
    method_access: Access | None,
) -> type:
    """Calls for functions that set different async methods and attributes to
    the class."""
    attributes = _get_meta_attributes(cls, raise_exceptions=False)
    collection = attributes['collection']
    index = attributes['index']

    _set_crud_methods(
        cls,
        add=add,
        get=get,
        get_all=get_all,
        update=update,
        delete=delete,
        add_batch=add_batch,
        method_access=method_access,
        get_list=get_list,
        async_methods=True,
    )

    if integer_fields is not None:
        _set_integer_fields_methods(
            cls, integer_fields=integer_fields, async_methods=True, method_access=method_access,
        )

    if array_fields is not None:
        _set_array_fields_methods(
            cls, array_fields=array_fields, async_methods=True, method_access=method_access,
        )

    if index is not None:
        asyncio.create_task(_create_index_async(index=index, collection=collection))

    if __methods__:
        _set__methods__(cls)
    return cls
