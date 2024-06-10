
from typing import Iterable

from mongorepo import exceptions
from mongorepo.utils import (
    _get_collection_and_dto,
    _get_dto_from_origin,
    _get_meta_attributes,
    get_default_values,
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
)


def _set_array_fields_methods(cls: type, array_fields: Iterable[str]) -> None:
    attributes = _get_collection_and_dto(cls)
    dto, collection = attributes['dto'], attributes['collection']
    dto_fields = get_default_values(dto)
    for field in array_fields:
        if field not in dto_fields:
            raise exceptions.MongoRepoException(message=f'{dto} does have "{field}" attribute')
        if dto_fields[field] is not list:
            print(dto_fields[field], type(dto_fields[field]))
            raise exceptions.MongoRepoException(message=f'"{field}" is not of type "list"')

        append_method = _update_list_field_method(
            dto_type=dto, collection=collection, field_name=field, command='$push'
        )
        remove_method = _update_list_field_method(
            dto_type=dto, collection=collection, field_name=field, command='$pull',
        )
        append_method.__name__ = f'append_to_{field}'
        remove_method.__name__ = f'remove_from_{field}'

        setattr(cls, append_method.__name__, append_method)
        setattr(cls, remove_method.__name__, remove_method)


def _set_integer_fields_methods(cls: type, integer_fields: Iterable[str]) -> None:
    attributes = _get_collection_and_dto(cls)
    dto, collection = attributes['dto'], attributes['collection']
    dto_fields = get_default_values(dto)
    for field in integer_fields:
        if field not in dto_fields:
            raise exceptions.MongoRepoException(message=f'{dto} does have "{field}" attribute')
        if dto_fields[field] is not int:
            raise exceptions.MongoRepoException(message=f'"{field}" is not integer field')

        incr_method = _update_integer_field_method(
            dto_type=dto, collection=collection, field_name=field, _weight=1,
        )
        decr_method = _update_integer_field_method(
            dto_type=dto, collection=collection, field_name=field, _weight=-1,
        )

        incr_method.__name__ = f'increment_{field}'
        decr_method.__name__ = f'decrement_{field}'

        setattr(cls, incr_method.__name__, incr_method)
        setattr(cls, decr_method.__name__, decr_method)


def _set_crud_methods(
    cls: type,
    add: bool = True,
    get: bool = True,
    delete: bool = True,
    update: bool = True,
    get_all: bool = True,
) -> None:
    """Set crud operations to repository"""
    attributes = _get_meta_attributes(cls, raise_exceptions=False)
    collection = attributes['collection']
    prefix = get_prefix(access=attributes['method_access'], cls=cls)

    dto = attributes['dto']
    if dto is None:
        dto = _get_dto_from_origin(cls)

    if add:
        setattr(cls, f'{prefix}add', _add_method(dto, collection=collection))
    if update:
        setattr(cls, f'{prefix}update', _update_method(dto, collection=collection))
    if get:
        setattr(cls, f'{prefix}get', _get_method(dto, collection=collection))
    if get_all:
        setattr(cls, f'{prefix}get_all', _get_all_method(dto, collection=collection))
    if delete:
        setattr(cls, f'{prefix}delete', _delete_method(dto, collection=collection))
