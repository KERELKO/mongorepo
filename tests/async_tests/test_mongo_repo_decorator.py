# type: ignore
import random

import pytest

from mongorepo.asyncio.decorators import async_mongo_repository
from mongorepo import exceptions

from tests.common import SimpleDTO, collection_for_simple_dto


async def test_all_methods_with_async_decorator():
    cl = collection_for_simple_dto(async_client=True)

    @async_mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl
            index = 'x'

    num = random.randint(1, 123456)

    repo = TestMongoRepository()
    new_dto: SimpleDTO = await repo.add(SimpleDTO(x='hey', y=num))
    assert new_dto.x == 'hey'

    updated_dto = await repo.update(SimpleDTO(x='hey all!', y=13), y=num)
    assert updated_dto.x == 'hey all!'

    async for dto in repo.get_all():
        assert isinstance(dto, SimpleDTO)

    dto = await repo.get(y=13)
    assert dto is not None

    is_deleted = await repo.delete(y=13)
    assert is_deleted is True

    dto = await repo.get(y=13)
    assert dto is None

    cl.drop()


async def test_cannot_initialize_class_if_dto_is_not_dataclass():

    class Bob:
        def __init__(self, name: str) -> None:
            self.name = name

    with pytest.raises(exceptions.NotDataClass):
        @async_mongo_repository
        class TestMongoRepository[Bob]:  # type:ignore
            class Meta:
                collection = collection_for_simple_dto(async_client=True)
                index = 'x'

        _ = TestMongoRepository()
