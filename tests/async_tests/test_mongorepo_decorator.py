# type: ignore
import random
import asyncio

import pytest

from mongorepo.asyncio.decorators import async_mongo_repository
from mongorepo import exceptions, Index

from tests.common import SimpleDTO, collection_for_simple_dto


async def test_all_methods_with_async_decorator():
    cl = collection_for_simple_dto(async_client=True)

    @async_mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl

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

    await repo.add(SimpleDTO(x='124', y=909))
    dtos = await repo.get_list()
    assert isinstance(dtos, list)
    assert isinstance(dtos[0], SimpleDTO)
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

        _ = TestMongoRepository()


async def test_can_create_index():
    cl = collection_for_simple_dto(async_client=True)

    @async_mongo_repository
    class TestMongoRepository:
        class Meta:
            collection = cl
            dto = SimpleDTO
            index = Index(field='x', name='async_index_for_x', unique=True)

    r = TestMongoRepository()
    await r.add(SimpleDTO(x='123', y=23))
    dto = await r.get(x='123')
    assert dto is not None

    await asyncio.sleep(2)

    assert 'async_index_for_x' in await cl.index_information()

    await cl.drop()
