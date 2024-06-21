from typing import Iterable

from mongorepo import exceptions
from mongorepo.base import Access
from mongorepo.utils import (
    _get_dto_from_origin,
    _get_meta_attributes,
    get_dto_type_hints,
    get_prefix,
)
from mongorepo._methods import (
    _update_integer_field_method,
    _update_list_field_method,
    _get_all_method,
    _get_method,
    _delete_method,
    _add_method,
    _update_method,
    _update_field_method,
    _pop_list_method,
    _get_list_method,
)
from mongorepo.asyncio._methods import (
    _update_field_method_async,
    _update_integer_field_method_async,
    _update_list_field_method_async,
    _add_method_async,
    _delete_method_async,
    _get_all_method_async,
    _get_method_async,
    _update_method_async,
    _pop_list_method_async,
    _get_list_method_async,
)


def _set_array_fields_methods(
    cls: type,
    array_fields: Iterable[str],
    async_methods: bool = False,
    method_access: Access | None = None,
) -> None:
    """
    Set base methods for array fields
    allow `method_access`, `async_method=True` to make this methods async
    """
    attributes = _get_meta_attributes(cls)
    dto, collection = attributes['dto'], attributes['collection']
    prefix = get_prefix(
        access=attributes['method_access'] if not method_access else method_access, cls=cls
    )
    dto_fields = get_dto_type_hints(dto)
    for field in array_fields:
        if field not in dto_fields:
            raise exceptions.MongoRepoException(message=f'{dto} does not have "{field}" attribute')
        if dto_fields[field] is not list:
            raise exceptions.MongoRepoException(message=f'"{field}" is not of type "list"')
        if async_methods:
            append_method = _update_list_field_method_async(
                dto_type=dto, collection=collection, field_name=field, command='$push'
            )
            remove_method = _update_list_field_method_async(
                dto_type=dto, collection=collection, field_name=field, command='$pull',
            )
            pop_method = _pop_list_method_async(
                dto_type=dto, collection=collection, field_name=field,
            )
        else:
            append_method = _update_list_field_method(
                dto_type=dto, collection=collection, field_name=field, command='$push'
            )
            remove_method = _update_list_field_method(
                dto_type=dto, collection=collection, field_name=field, command='$pull',
            )
            pop_method = _pop_list_method(dto_type=dto, collection=collection, field_name=field)

        pop_method.__name__ = f'{prefix}{field}__pop'
        append_method.__name__ = f'{prefix}{field}__append'
        remove_method.__name__ = f'{prefix}{field}__remove'

        setattr(cls, pop_method.__name__, pop_method)
        setattr(cls, append_method.__name__, append_method)
        setattr(cls, remove_method.__name__, remove_method)


def _set_integer_fields_methods(
    cls: type,
    integer_fields: Iterable[str],
    async_methods: bool = False,
    method_access: Access | None = None,
) -> None:
    """
    Set base methods for integer fields,
    allow `method_access`, `async_method=True` to make this methods async
    """
    attributes = _get_meta_attributes(cls)
    dto, collection = attributes['dto'], attributes['collection']
    prefix = get_prefix(
        access=attributes['method_access'] if not method_access else method_access, cls=cls
    )
    dto_fields = get_dto_type_hints(dto)
    for field in integer_fields:
        if field not in dto_fields:
            raise exceptions.MongoRepoException(message=f'{dto} does not have "{field}" attribute')
        if dto_fields[field] is not int:
            raise exceptions.MongoRepoException(message=f'"{field}" is not integer field')
        if async_methods:
            incr_method = _update_integer_field_method_async(
                dto_type=dto, collection=collection, field_name=field, _weight=1
            )
            decr_method = _update_integer_field_method_async(
                dto_type=dto, collection=collection, field_name=field, _weight=-1
            )
        else:
            incr_method = _update_integer_field_method(
                dto_type=dto, collection=collection, field_name=field, _weight=1
            )
            decr_method = _update_integer_field_method(
                dto_type=dto, collection=collection, field_name=field, _weight=-1
            )

        incr_method.__name__ = f'{prefix}increment_{field}'
        decr_method.__name__ = f'{prefix}decrement_{field}'

        setattr(cls, incr_method.__name__, incr_method)
        setattr(cls, decr_method.__name__, decr_method)


def _set_crud_methods(
    cls: type,
    add: bool = True,
    get: bool = True,
    delete: bool = True,
    update: bool = True,
    get_list: bool = True,
    get_all: bool = True,
    update_field: bool = False,
    async_methods: bool = False,
    method_access: Access | None = None,
) -> None:
    """
    Set CRUD operations to the class
    allow `method_access`, `async_method=True` to make added methods async
    """
    attributes = _get_meta_attributes(cls, raise_exceptions=False)
    collection = attributes['collection']
    prefix = get_prefix(
        access=attributes['method_access'] if not method_access else method_access, cls=cls
    )
    id_field = attributes['id_field']
    dto = attributes['dto']
    if dto is None:
        dto = _get_dto_from_origin(cls)

    if add:
        f = _add_method_async if async_methods else _add_method
        setattr(cls, f'{prefix}add', f(dto, collection=collection, id_field=id_field))  # type: ignore # noqa
    if update:
        f = _update_method_async if async_methods else _update_method
        setattr(cls, f'{prefix}update', f(dto, collection=collection))  # type: ignore
    if get:
        f = _get_method_async if async_methods else _get_method
        setattr(cls, f'{prefix}get', f(dto, collection=collection, id_field=id_field))  # type: ignore # noqa
    if get_all:
        f = _get_all_method_async if async_methods else _get_all_method
        setattr(cls, f'{prefix}get_all', f(dto, collection=collection, id_field=id_field))  # type: ignore # noqa
    if get_list:
        f = _get_list_method_async if async_methods else _get_list_method
        setattr(cls, f'{prefix}get_list', f(dto, collection=collection, id_field=id_field))  # type: ignore # noqa
    if delete:
        f = _delete_method_async if async_methods else _delete_method
        setattr(cls, f'{prefix}delete', f(dto, collection=collection))  # type: ignore
    if update_field:
        f = _update_field_method_async if async_methods else _update_field_method
        setattr(cls, f'{prefix}update_field', f(dto, collection=collection, id_field=id_field))  # type: ignore # noqa
