from dataclasses import fields, is_dataclass
from typing import Any, Type, get_args

import pymongo
from pymongo.collection import Collection

from mongorepo._methods import (
    _get_method,
    _get_all_method,
    _update_method,
    _add_method,
    _delete_method,
)
from mongorepo import DTO, Access, Index
from mongorepo import exceptions


def _handle_cls(
    cls,
    add: bool,
    get: bool,
    get_all: bool,
    update: bool,
    delete: bool,
) -> type:
    attributes = _get_meta_attributes(cls, raise_exceptions=False)
    dto = attributes['dto']
    if not dto:
        dto = _get_dto_type_from_origin(cls)
        if not is_dataclass(dto):
            raise exceptions.NotDataClass
    collection = attributes['collection']
    index = attributes['index']
    prefix = get_prefix(access=attributes['method_access'], cls=cls)

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
    if index is not None:
        _create_index(index=index, collection=collection)
    return cls


def _get_meta_attributes(cls, raise_exceptions: bool = True) -> dict[str, Any]:
    attributes = {}
    try:
        meta = cls.__dict__['Meta']
    except (AttributeError, KeyError) as e:
        raise exceptions.NoMetaException from e
    try:
        dto = meta.dto
        attributes['dto'] = dto
    except AttributeError as e:
        if raise_exceptions:
            raise exceptions.NoDTOTypeException from e
        else:
            attributes['dto'] = None
    try:
        collection = meta.collection
        attributes['collection'] = collection
    except AttributeError as e:
        if raise_exceptions:
            raise exceptions.NoCollectionException from e
        else:
            attributes['collection'] = None

    # Optional variables
    index: Index | str | None = getattr(meta, 'index', None)
    attributes['index'] = index

    method_access: Access | None = getattr(meta, 'method_access', None)
    attributes['method_access'] = method_access

    substitute: dict[str, str] | None = getattr(meta, 'substitute', None)
    attributes['substitute'] = substitute

    return attributes


def get_default_values(dto: Type[DTO] | DTO) -> dict[str, Any]:
    """Returns dictionary of default values for a dataclass or dataclass instance"""
    default_values = {}
    for field_info in fields(dto):
        if field_info.default is not field_info.default_factory:
            default_values[field_info.name] = field_info.default
        else:
            default_values[field_info.name] = field_info.default_factory()  # type: ignore
    return default_values


def _create_index(index: Index | str, collection: Collection) -> None:
    """
    ### Creates an index for the collection
    * index parameter can be string or mongorepo.Index
    * If index is string, create standard mongodb index
    * If it's `mongorepo.Index` creates index with user's settings
    """
    if isinstance(index, str):
        collection.create_index(index)
        return
    index_name = f'index_{index.field}_1'
    if index.name:
        index_name = index.name
    direction = pymongo.DESCENDING if index.desc else pymongo.ASCENDING
    collection.create_index(
        [(index.field, direction)],
        name=index_name,
        unique=index.unique,
    )


def get_prefix(access: Access | None, cls: type | None = None) -> str:
    """
    Returns string prefix according to Access value,
    * it can be `'_'`, `'__'`, `_{cls.__name__}__` or `''`
    """
    match access:
        case Access.PRIVATE:
            prefix = f'_{cls.__name__}__' if cls else '__'
        case Access.PROTECTED:
            prefix = '_'
        case Access.PUBLIC | None:
            prefix = ''
    return prefix


def _get_dto_type_from_origin(cls) -> type:
    try:
        if not hasattr(cls, '__orig_bases__'):
            raise exceptions.NoDTOTypeException
        dto_type: type = get_args(cls.__orig_bases__[0])[0]
    except IndexError:
        raise exceptions.NoDTOTypeException
    if dto_type is DTO:
        raise exceptions.NoDTOTypeException
    return dto_type
