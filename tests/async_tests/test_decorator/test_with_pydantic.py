# mypy: disable-error-code="attr-defined"
import random

from pydantic import BaseModel

from mongorepo import RepositoryConfig, async_repository
from tests.common import in_async_collection


async def test_methods_for_pydantic_entity_with_async_decorator() -> None:

    class SimpleEntity(BaseModel):
        x: str
        y: int

    async with in_async_collection(SimpleEntity) as cl:
        @async_repository(
            config=RepositoryConfig(
                entity_type=SimpleEntity,
                collection=cl,
                to_document_converter=lambda entity: entity.model_dump(),
                to_entity_converter=lambda data, model: model(**data),
            ),
        )
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
