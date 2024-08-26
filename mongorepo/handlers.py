import inspect
from typing import Callable

from mongorepo.asyncio.utils import _run_asyncio_create_index
from mongorepo.base import Access
from mongorepo.setters import (
    _set_array_fields_methods,
    _set_crud_methods,
    _set_integer_fields_methods,
)
from mongorepo.utils import _get_meta_attributes, raise_exc, create_index
from mongorepo import exceptions
from mongorepo._methods import METHOD_NAME__CALLABLE
from mongorepo._substitute import _substitute_method
from mongorepo.asyncio._methods import METHOD_NAME__CALLABLE as METHOD_NAME__CALLABLE_ASYNC


def _handle_mongo_repository(
    cls,
    add: bool,
    get: bool,
    add_batch: bool,
    get_all: bool,
    update: bool,
    delete: bool,
    get_list: bool,
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
        add_batch=add_batch,
        method_access=method_access,
    )

    if index is not None:
        create_index(index=index, collection=collection)

    if integer_fields is not None:
        _set_integer_fields_methods(cls, integer_fields=integer_fields, method_access=method_access)

    if array_fields is not None:
        _set_array_fields_methods(cls, array_fields=array_fields, method_access=method_access)

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
        _run_asyncio_create_index(index=index, collection=collection)
    return cls


def _handle_implements(
    base_cls: type,
    cls: type,
    **substitute: str | Callable,
) -> type:
    attrs = _get_meta_attributes(cls)
    if not substitute:
        substitute = attrs['substitute'] if attrs['substitute'] is not None else raise_exc(
            exceptions.MongoRepoException(message='No "substitute" in Meta class')
        )
    dto_type = attrs['dto']
    collection = attrs['collection']
    id_field = attrs['id_field']
    for mongorepo_method_name, _generic_method in substitute.items():
        if inspect.isfunction(_generic_method) or inspect.ismethod(_generic_method):
            generic_method: Callable = _generic_method  # type: ignore
        elif isinstance(_generic_method, str):
            generic_method: Callable | None = getattr(
                base_cls, _generic_method, None
            )
            if generic_method is None or not inspect.isfunction(generic_method):
                raise exceptions.InvalidMethodNameException(_generic_method)

        is_async: bool = inspect.iscoroutinefunction(generic_method)

        if mongorepo_method_name not in METHOD_NAME__CALLABLE:
            raise exceptions.InvalidMethodNameException(mongorepo_method_name)
        if is_async:
            mongorepo_method: Callable = METHOD_NAME__CALLABLE_ASYNC[mongorepo_method_name]
        else:
            mongorepo_method: Callable = METHOD_NAME__CALLABLE[
                mongorepo_method_name
            ]

        setattr(
            cls,
            generic_method.__name__,
            _substitute_method(
                mongorepo_method,
                generic_method,
                dto_type,
                collection,
                id_field=id_field,
            ),
        )

    return cls
