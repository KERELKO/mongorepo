import asyncio
import pymongo
from mongorepo import Index
from motor.motor_asyncio import AsyncIOMotorCollection


def _run_asyncio_create_index(index: Index | str, collection: AsyncIOMotorCollection) -> None:
    """
    Tries to create an index for `AsyncIOMotorCollection` in async loop or after
    """
    loop = asyncio.get_running_loop()
    if loop.is_running():
        asyncio.create_task(_create_index_async(index=index, collection=collection))
    else:
        loop.run_until_complete(_create_index_async(index=index, collection=collection))


async def _create_index_async(index: Index | str, collection: AsyncIOMotorCollection) -> None:
    """
    ### Creates an index for the collection
    * index parameter can be string or mongorepo.Index
    * If index is string, create standard mongodb index
    * If it's `mongorepo.Index` creates index with user's settings
    """
    if isinstance(index, str):
        await collection.create_index(index)
        return
    index_name = f'index_{index.field}'
    if index.name:
        index_name = index.name
    direction = pymongo.DESCENDING if index.desc else pymongo.ASCENDING
    await collection.create_index(
        [(index.field, direction)],
        name=index_name,
        unique=index.unique,
    )
