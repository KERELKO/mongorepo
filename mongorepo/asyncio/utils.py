import asyncio
from dataclasses import is_dataclass

import pymongo
from mongorepo import exceptions
from mongorepo.asyncio._methods import (
    _get_all_method_async,
    _get_method_async,
    _update_method_async,
    _delete_method_async,
    _add_method_async,
)
from mongorepo.base import Index
from mongorepo.utils import _get_dto_type_from_origin, _get_meta_attributes, get_prefix
from motor.motor_asyncio import AsyncIOMotorCollection


def _handle_cls_async(
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
        setattr(cls, f'{prefix}add', _add_method_async(dto, collection=collection))
    if update:
        setattr(cls, f'{prefix}update', _update_method_async(dto, collection=collection))
    if get:
        setattr(cls, f'{prefix}get', _get_method_async(dto, collection=collection))
    if get_all:
        setattr(cls, f'{prefix}get_all', _get_all_method_async(dto, collection=collection))
    if delete:
        setattr(cls, f'{prefix}delete', _delete_method_async(dto, collection=collection))
    if index is not None:
        if asyncio.get_event_loop().is_running():
            asyncio.ensure_future(
                _create_index_async(index=index, collection=collection)
            )
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_create_index_async(index=index, collection=collection))
    return cls


async def _create_index_async(index: Index | str, collection: AsyncIOMotorCollection) -> None:
    """
    ### Creates an index for the collection
    * index parameter can be string or mongorepo.base.Index
    * If index is string, create standard mongodb index
    * If it's `mongorepo.base.Index` creates index with user's settings
    """
    if isinstance(index, str):
        await collection.create_index(index)
        return
    index_name = f'index_{index.field}_1'
    if index.name:
        index_name = index.name
    if index_name in await collection.index_information():
        return
    direction = pymongo.DESCENDING if index.desc else pymongo.ASCENDING
    await collection.create_index(
        [(index.field, direction)],
        name=index_name,
        unique=index.unique,
    )
