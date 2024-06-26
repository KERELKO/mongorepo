import inspect

from mongorepo.asyncio.utils import _run_asyncio_create_index
from mongorepo.base import Access
from mongorepo.setters import (
    _set_array_fields_methods,
    _set_crud_methods,
    _set_integer_fields_methods,
)
from mongorepo.utils import _get_meta_attributes, raise_exc, create_index
from mongorepo import exceptions
from mongorepo._methods import _substitute_method


def _handle_cls(
    cls,
    add: bool,
    get: bool,
    get_all: bool,
    update: bool,
    delete: bool,
    get_list: bool,
    update_field: bool,
    integer_fields: list[str] | None,
    array_fields: list[str] | None,
    method_access: Access | None,
) -> type:
    """
    Calls for functions that set different methods and attributes to the class
    """
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
        update_field=update_field,
        method_access=method_access,
    )

    if index is not None:
        create_index(index=index, collection=collection)

    if integer_fields is not None:
        _set_integer_fields_methods(cls, integer_fields=integer_fields, method_access=method_access)

    if array_fields is not None:
        _set_array_fields_methods(cls, array_fields=array_fields, method_access=method_access)

    return cls


def _handle_cls_async(
    cls,
    add: bool,
    get: bool,
    get_all: bool,
    get_list: bool,
    update: bool,
    delete: bool,
    update_field: bool,
    integer_fields: list[str] | None,
    array_fields: list[str] | None,
    method_access: Access | None,
) -> type:
    """
    Calls for functions that set different async methods and attributes to the class
    """
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
        update_field=update_field,
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
        _run_asyncio_create_index(index=index, collection=collection)
    return cls


def _handle_implements(generic_cls: type, cls: type) -> type:
    attrs = _get_meta_attributes(cls)
    substitute = attrs['substitute'] if attrs['substitute'] is not None else raise_exc(
        exceptions.MongoRepoException(message='No "substitue" in Meta class')
    )
    dto_type = attrs['dto']
    collection = attrs['collection']
    id_field = attrs['id_field']
    for mongorepo_method_name, generic_method_name in substitute.items():
        generic_method = getattr(generic_cls, generic_method_name, None)

        if generic_method is None or not inspect.isfunction(generic_method):
            raise exceptions.InvalidMethodNameException(generic_method_name)
        setattr(
            cls, generic_method_name,
            _substitute_method(
                mongorepo_method_name,
                generic_method,
                dto_type,
                collection,
                id_field=id_field,
            ),
        )

    return cls
