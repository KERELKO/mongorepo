# mypy: disable-error-code="attr-defined"
from abc import ABC
from dataclasses import dataclass
from typing import Generic, Protocol

from mongorepo import Entity, MethodAccess, RepositoryConfig
from mongorepo.decorators import mongo_repository
from tests.common import EntityWithID, in_collection


def test_decorator_with_abstract_class() -> None:
    # Suppose we have abstract repository in our architecture
    # but mongo_repository's methods does not fit to it
    # there is the simplest way to fix it

    # NOTE: we can't use @abstractmethod because it's will raise an error
    # you can still use typing.Protocol, tho
    class AbstractUserRepository(Generic[Entity], ABC):
        def get_by_username(self, username: str) -> Entity | None:
            raise NotImplementedError

        def create(self, entity: Entity) -> Entity:
            raise NotImplementedError

    @dataclass
    class UserEntity:
        username: str
        password: str

    with in_collection(UserEntity) as cl:
        # Solution
        @mongo_repository(
            config=RepositoryConfig(entity_type=UserEntity, collection=cl, method_access=MethodAccess.PROTECTED),
        )
        class MongoUserRepository(AbstractUserRepository[UserEntity]):
            def get_by_username(self, username: str) -> UserEntity | None:
                # decorator adds protected method "_get"
                entity = self._get(username=username)
                return entity

            def create(self, entity: UserEntity) -> UserEntity:
                new_dto = self._add(entity=entity)
                return new_dto

        repo = MongoUserRepository()

        entity = UserEntity(username='admin', password='1234')
        new_user: UserEntity = repo.create(entity=entity)
        assert new_user.username == 'admin' and new_user.password == '1234'

        resolved_user: UserEntity = repo.get_by_username(username='admin')  # type: ignore[assignment]
        assert resolved_user.username == 'admin'


def test_decorator_with_protocol_and_dto_with_id() -> None:
    class IRepository(Protocol):
        def add(self, entity: EntityWithID) -> None:
            ...

        def get_by_id(self, id: str) -> EntityWithID | None:
            ...

    with in_collection(EntityWithID) as cl:
        @mongo_repository(
            config=RepositoryConfig(entity_type=EntityWithID, collection=cl, method_access=MethodAccess.PROTECTED),
        )
        class MongoRepository:
            def get_by_id(self, id: str) -> EntityWithID | None:
                entity = self._get(_id=id)
                return entity

            def add(self, entity: EntityWithID) -> None:
                self._add(entity=entity)

        repo = MongoRepository()
        entity = EntityWithID(x='one two', y=10)
        dto_id: str = entity._id
        repo.add(entity)

        # get entity with generated id
        resolved_dto: EntityWithID | None = repo.get_by_id(id=dto_id)
        assert resolved_dto is not None
        assert resolved_dto.y == 10

        assert resolved_dto._id == dto_id
