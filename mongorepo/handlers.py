

from mongorepo.setters import (
    _set_array_fields_methods,
    _set_crud_methods,
    _set_integer_fields_methods,
)
from mongorepo.utils import _get_meta_attributes, create_index


def _handle_cls(
    cls,
    add: bool,
    get: bool,
    get_all: bool,
    update: bool,
    delete: bool,
    update_field: bool,
    integer_fields: list[str] | None,
    array_fields: list[str] | None,
) -> type:
    attributes = _get_meta_attributes(cls, raise_exceptions=False)
    collection = attributes['collection']
    index = attributes['index']

    _set_crud_methods(cls, add=add, get=get, get_all=get_all, update=update, delete=delete)

    if index is not None:
        create_index(index=index, collection=collection)

    if integer_fields is not None:
        _set_integer_fields_methods(cls, integer_fields=integer_fields)

    if array_fields is not None:
        _set_array_fields_methods(cls, array_fields=array_fields)

    return cls
