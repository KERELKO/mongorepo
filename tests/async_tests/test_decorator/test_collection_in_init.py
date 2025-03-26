import pytest
from motor.motor_asyncio import AsyncIOMotorCollection

import mongorepo
from tests.common import SimpleDTO, in_async_collection


@pytest.mark.skip
async def test_can_use_collection_in_init():
    async with in_async_collection(SimpleDTO) as collection:

        @mongorepo.use_collection(collection)
        @mongorepo.async_repository()
        class Repository:
            class Meta:
                dto = SimpleDTO

            def __init__(self, collection: AsyncIOMotorCollection) -> None:
                self.mongorepo_collection = collection

        repo = Repository(collection)

        await repo.add(SimpleDTO(x='123', y=123))  # type: ignore

        dto: SimpleDTO | None = await repo.get(x='123')  # type: ignore
        assert dto is not None
        assert dto.x == '123'
