# type: ignore
import random

import pytest

from mongorepo import async_repository, exceptions
from tests.common import SimpleEntity, r, in_async_collection, custom_collection


async def test_all_methods_with_async_decorator():

    async with in_async_collection(SimpleEntity) as cl:
        @async_repository
        class TestMongoRepository:
            class Meta:
                entity = SimpleEntity
                collection = cl

        num = random.randint(1, 123456)

        repo = TestMongoRepository()
        new_dto: SimpleEntity = await repo.add(SimpleEntity(x='hey', y=num))
        assert new_dto.x == 'hey'

        updated_dto = await repo.update(SimpleEntity(x='hey all!', y=13), y=num)
        assert updated_dto.x == 'hey all!'

        async for entity in repo.get_all():
            assert isinstance(entity, SimpleEntity)

        entity = await repo.get(y=13)
        assert entity is not None

        is_deleted = await repo.delete(y=13)
        assert is_deleted is True

        entity = await repo.get(y=13)
        assert entity is None

        await repo.add(SimpleEntity(x='124', y=909))
        dtos = await repo.get_list()
        assert isinstance(dtos, list)
        assert isinstance(dtos[0], SimpleEntity)


async def test_cannot_initialize_class_if_dto_is_not_dataclass():

    class Bob:
        def __init__(self, name: str) -> None:
            self.name = name

    with pytest.raises(exceptions.NoDTOTypeException):
        @async_repository
        class TestMongoRepository[Bob]:  # type: ignore
            class Meta:
                collection = custom_collection(Bob, async_client=True)

        _ = TestMongoRepository()


async def test_get_list_with_add_batch_methods_with_decorator():

    async with in_async_collection(SimpleEntity) as cl:
        @async_repository(add_batch=True, get_list=True)
        class TestMongoRepository:
            class Meta:
                entity = SimpleEntity
                collection = cl

        repo = TestMongoRepository()

        await repo.add_batch(
            [SimpleEntity(x='hey', y=r()), SimpleEntity(x='second hey!', y=r())],
        )

        dto_list = await repo.get_list(offset=0, limit=10)
        for entity in dto_list:
            assert entity
            assert isinstance(entity, SimpleEntity)

        async for entity in repo.get_all():
            assert isinstance(entity, SimpleEntity)
