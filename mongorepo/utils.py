from dataclasses import fields
from typing import Any, Type

from mongorepo._methods import (
    _get_method,
    _get_all_method,
    _update_method,
    _create_method,
    _delete_method,
)
from mongorepo.asyncio._methods import (
    _get_all_method_async,
    _get_method_async,
    _update_method_async,
    _delete_method_async,
    _create_method_async,
)
from mongorepo.base import DTO


def _handle_cls(
    cls,
    create: bool,
    get: bool,
    get_all: bool,
    update: bool,
    delete: bool,
    async_: bool = False
) -> type:
    attributes = _get_repo_attributes(cls)
    dto = attributes['dto']
    collection = attributes['collection']
    if create:
        if not async_:
            setattr(cls, 'create', _create_method(dto, collection=collection))
        else:
            setattr(cls, 'create', _create_method_async(dto, collection=collection))
    if update:
        if not async_:
            setattr(cls, 'update', _update_method(dto, collection=collection))
        else:
            setattr(cls, 'update', _update_method_async(dto, collection=collection))
    if get:
        if not async_:
            setattr(cls, 'get', _get_method(dto, collection=collection))
        else:
            setattr(cls, 'get', _get_method_async(dto, collection=collection))
    if get_all:
        if not async_:
            setattr(cls, 'get_all', _get_all_method(dto, collection=collection))
        else:
            setattr(cls, 'get_all', _get_all_method_async(dto, collection=collection))
    if delete:
        if not async_:
            setattr(cls, 'delete', _delete_method(dto, collection=collection))
        else:
            setattr(cls, 'delete', _delete_method_async(dto, collection=collection))
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
    return attributes


def get_default_values(dto: Type[DTO] | DTO) -> dict[str, Any]:
    default_values = {}
    for field_info in fields(dto):  # type: ignore
        if field_info.default is not field_info.default_factory:
            default_values[field_info.name] = field_info.default
        else:
            default_values[field_info.name] = field_info.default_factory()  # type: ignore
    return default_values
