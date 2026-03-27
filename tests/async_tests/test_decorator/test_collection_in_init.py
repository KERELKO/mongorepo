import pytest
from motor.motor_asyncio import AsyncIOMotorCollection

import mongorepo
from tests.common import SimpleEntity, in_async_collection


@pytest.mark.skip
async def test_can_use_collection_in_init():
    async with in_async_collection(SimpleEntity) as collection:

        @mongorepo.use_collection(collection)
        @mongorepo.async_repository()
        class Repository:
            class Meta:
                entity = SimpleEntity

            def __init__(self, collection: AsyncIOMotorCollection) -> None:
                self.mongorepo_collection = collection

        repo = Repository(collection)

        await repo.add(SimpleEntity(x='123', y=123))  # type: ignore

        entity: SimpleEntity | None = await repo.get(x='123')  # type: ignore
        assert entity is not None
        assert entity.x == '123'
