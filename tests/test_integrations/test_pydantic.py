# mypy: disable-error-code="attr-defined"
import random
import uuid
from abc import ABC, abstractmethod
from typing import cast

from pydantic import BaseModel, Field

from mongorepo import RepositoryConfig, async_repository
from mongorepo.implement import implement
from mongorepo.implement.methods import (
    AddMethod,
    GetMethod,
    ListAppendMethod,
    ListItemsMethod,
)
from mongorepo.modifiers.base import RaiseExceptionModifier
from mongorepo.types.field_alias import FieldAlias
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


async def test_specific_methods_in_implement_decorator_for_msgspec_entity() -> None:

    class Friend(BaseModel):
        id: str
        name: str

    class User(BaseModel):
        id: str
        friends: list[Friend] = Field(default_factory=list)

    class UserRepository(ABC):
        @abstractmethod
        async def get(self, id: str) -> User:
            ...

        @abstractmethod
        async def add(self, user: User) -> None:
            ...

        @abstractmethod
        async def add_friend(self, user_id: str, friend: Friend):
            ...

        @abstractmethod
        async def get_friends(self, user_id: str, offset: int, limit: int) -> list[Friend]:
            ...

    raise_exc_on_none = RaiseExceptionModifier(ValueError, None)

    async with in_async_collection(User) as cl:
        @implement(
            GetMethod(UserRepository.get, ["id"], modifiers=(raise_exc_on_none,)),
            AddMethod(UserRepository.add, entity='user'),
            ListAppendMethod(
                UserRepository.add_friend,
                field='friends',
                value='friend',
                filters=[uidfa := FieldAlias('id', 'user_id')],
            ),
            ListItemsMethod(
                UserRepository.get_friends,
                field='friends',
                filters=[uidfa],
                offset='offset',
                limit='limit',
            ),
            config=RepositoryConfig(
                entity_type=User,
                collection=cl,
                to_document_converter=lambda entity: entity.model_dump(),
                to_entity_converter=lambda data, model: model(**data),
            ),
        )
        class MongoUserRepository:
            ...

        repo = cast(UserRepository, MongoUserRepository())

        user = User(id=str(uuid.uuid4()), friends=[Friend(id=str(uuid.uuid4()), name='Bob')])

        await repo.add(user)

        added_user = await repo.get(user.id)

        assert added_user.friends[0].id == user.friends[0].id

        await repo.add_friend(user.id, Friend(id=str(uuid.uuid4()), name='Billy'))

        friends = await repo.get_friends(user.id, offset=0, limit=20)

        assert len(friends) == 2
