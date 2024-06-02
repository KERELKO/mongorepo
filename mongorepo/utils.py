from typing import Any

from mongorepo._methods import (
    _get_method,
    _get_all_method,
    _get_by_id_method,
    _update_method,
    _create_method,
    _delete_by_id_method,
)


def _manage(
    cls,
    create: bool,
    get_by_id: bool,
    update: bool,
    delete_by_id: bool,
    get: bool,
    get_all: bool,
) -> type:
    attributes = _get_repo_attributes(cls)
    dto = attributes['dto']
    collection = attributes['collection']
    if create:
        setattr(cls, 'create', _create_method(dto, collection=collection))
    if get_by_id:
        setattr(cls, 'get_by_id', _get_by_id_method(dto, collection=collection))
    if update:
        setattr(cls, 'update', _update_method(dto, collection=collection))
    if delete_by_id:
        setattr(cls, 'delete_by_id', _delete_by_id_method(dto, collection=collection))
    if get:
        setattr(cls, 'get', _get_method(dto, collection=collection))
    if get_all:
        setattr(cls, 'get_all', _get_all_method(dto, collection=collection))
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
