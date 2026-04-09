# mypy: disable-error-code="attr-defined"
from dataclasses import dataclass

import pytest
from adaptix import Retort

from mongorepo import RepositoryConfig, async_repository
from mongorepo.exceptions import EntityIsNotDataclass
from tests.common import SimpleEntity, in_async_collection


async def test_repository_works_without_converters():
    async with in_async_collection(SimpleEntity) as cl:
        @async_repository(
            config=RepositoryConfig(
                entity_type=SimpleEntity,
                collection=cl,
            ),
        )
        class TestMongoRepository:
            ...

        repo = TestMongoRepository()

        entity = SimpleEntity(x="1", y=1)
        await repo.add(entity)

        entity = await repo.get(y=1)

        assert entity is not None

        assert entity.x == "1" and entity.y == 1


async def test_repository_works_with_converters() -> None:

    @dataclass
    class Entity:
        id: int
        messages: list[str]

    def to_document_converter(entity: Entity) -> dict:
        return {
            "entity_id": entity.id,
            "messages": entity.messages,
        }

    def from_document_converter(data: dict, entity_type: type[Entity]) -> Entity:
        return Entity(
            id=data["entity_id"],
            messages=data["messages"],
        )

    async with in_async_collection(Entity) as cl:
        @async_repository(
            config=RepositoryConfig(
                entity_type=Entity,
                collection=cl,
                to_document_converter=to_document_converter,  # type: ignore[arg-type]
                to_entity_converter=from_document_converter,  # type: ignore[arg-type]
            ),
        )
        class EntityMongoRepository:
            ...

        repo = EntityMongoRepository()

        messages = ["1", "2"]
        entity = Entity(id=1, messages=messages)
        await repo.add(entity)

        entity = await repo.get(entity_id=1)

        assert entity is not None
        assert entity.id == 1
        assert hasattr(entity, "entity_id") is False
        assert entity.messages == messages


async def test_repository_works_with_adaptix_converters() -> None:

    @dataclass
    class Entity:
        id: int
        text: str

    retort = Retort()

    async with in_async_collection(Entity) as cl:
        @async_repository(
            config=RepositoryConfig(
                entity_type=Entity,
                collection=cl,
                to_entity_converter=retort.load,
            ),
        )
        class EntityMongoRepository:
            ...

        repo = EntityMongoRepository()

        entity = Entity(id=1, text='123')
        await repo.add(entity)

        entity = await repo.get(id=1)

        assert entity is not None
        assert entity.id == 1
        assert entity.text == '123'


async def cannot_create_repository_without_converters() -> None:
    class Entity:
        def __init__(self, id: int):
            self.id = id

    async with in_async_collection(Entity) as cl:

        with pytest.raises(EntityIsNotDataclass):
            @async_repository(config=RepositoryConfig(entity_type=Entity, collection=cl))
            class EntityMongoRepository:
                ...
