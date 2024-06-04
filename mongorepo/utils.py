from dataclasses import fields
from typing import Any, Type

import pymongo
from pymongo.collection import Collection

from mongorepo._methods import (
    _get_method,
    _get_all_method,
    _update_method,
    _add_method,
    _delete_method,
)
from mongorepo.asyncio._methods import (
    _get_all_method_async,
    _get_method_async,
    _update_method_async,
    _delete_method_async,
    _add_method_async,
)
from mongorepo.base import DTO, Index


def _handle_cls(
    cls,
    add: bool,
    get: bool,
    get_all: bool,
    update: bool,
    delete: bool,
) -> type:
    attributes = _get_repo_attributes(cls)
    dto = attributes['dto']
    collection = attributes['collection']
    index = attributes['index']
    if add:
        setattr(cls, 'add', _add_method(dto, collection=collection))
    if update:
        setattr(cls, 'update', _update_method(dto, collection=collection))
    if get:
        setattr(cls, 'get', _get_method(dto, collection=collection))
    if get_all:
        setattr(cls, 'get_all', _get_all_method(dto, collection=collection))
    if delete:
        setattr(cls, 'delete', _delete_method(dto, collection=collection))
    if index is not None:
        _create_index(index=index, collection=collection)
    return cls


def _handle_cls_async(
    cls,
    add: bool,
    get: bool,
    get_all: bool,
    update: bool,
    delete: bool,
) -> type:
    attributes = _get_repo_attributes(cls)
    dto = attributes['dto']
    collection = attributes['collection']
    index = attributes['index']
    if add:
        setattr(cls, 'add', _add_method_async(dto, collection=collection))
    if update:
        setattr(cls, 'update', _update_method_async(dto, collection=collection))
    if get:
        setattr(cls, 'get', _get_method_async(dto, collection=collection))
    if get_all:
        setattr(cls, 'get_all', _get_all_method_async(dto, collection=collection))
    if delete:
        setattr(cls, 'delete', _delete_method_async(dto, collection=collection))
    if index is not None:
        _create_index(index=index, collection=collection)
    return cls


def _get_repo_attributes(cls) -> dict[str, Any]:
    attributes = {}
    try:
        meta = cls.__dict__['Meta']
    except AttributeError as e:
        raise AttributeError('Decorated class does not have "Meta" class inside') from e
    try:
        dto = meta.dto
        attributes['dto'] = dto
    except AttributeError as e:
        raise AttributeError('Decorated class does not have DTO type inside') from e
    try:
        collection = meta.collection
        attributes['collection'] = collection
    except AttributeError as e:
        raise AttributeError('Decorated class does not have "collection" inside') from e

    index: Index | str | None = getattr(meta, 'index', None)
    attributes['index'] = index

    return attributes


def get_default_values(dto: Type[DTO] | DTO) -> dict[str, Any]:
    default_values = {}
    for field_info in fields(dto):  # type: ignore
        if field_info.default is not field_info.default_factory:
            default_values[field_info.name] = field_info.default
        else:
            default_values[field_info.name] = field_info.default_factory()  # type: ignore
    return default_values


def _create_index(index: Index | str, collection: Collection) -> None:
    if isinstance(index, str):
        collection.create_index(index)
        return
    index_name = f'index_{index.field}_1'
    if index.name:
        index_name = index.name
    if index_name in collection.index_information():
        return
    direction = pymongo.DESCENDING if index.desc else pymongo.ASCENDING
    collection.create_index(
        [(index.field, direction)],
        name=index_name,
        unique=index.unique
    )
