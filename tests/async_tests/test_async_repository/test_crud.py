# mypy: disable-error-code="attr-defined"
import random

from mongorepo import RepositoryConfig, async_repository
from tests.common import SimpleEntity, in_async_collection, r


async def test_all_methods_with_async_decorator() -> None:
    async with in_async_collection(SimpleEntity) as cl:
        @async_repository(config=RepositoryConfig(entity_type=SimpleEntity, collection=cl))
        class TestMongoRepository:
            ...

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


async def test_get_list_with_add_batch_methods_with_decorator():

    async with in_async_collection(SimpleEntity) as cl:
        @async_repository(
            add_batch=True, get_list=True, config=RepositoryConfig(entity_type=SimpleEntity, collection=cl),
        )
        class TestMongoRepository:
            ...

        repo = TestMongoRepository()

        await repo.add_batch(
            [SimpleEntity(x='hey', y=r()), SimpleEntity(x='second hey!', y=r())],
        )

        entity_list = await repo.get_list(offset=0, limit=10)
        for entity in entity_list:
            assert entity
            assert isinstance(entity, SimpleEntity)

        async for entity in repo.get_all():
            assert isinstance(entity, SimpleEntity)
