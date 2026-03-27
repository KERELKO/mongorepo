# type: ignore
from dataclasses import dataclass
from typing import Generic, Protocol

from abc import ABC
from mongorepo import Access, Entity
from mongorepo.decorators import mongo_repository
from tests.common import (
    EntityWithID,
    in_collection,
)


def test_decorator_with_abstract_class():
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
    class UserDTO:
        username: str
        password: str

    with in_collection(UserDTO) as cl:
        # Solution
        @mongo_repository
        class MongoUserRepository(AbstractUserRepository[UserDTO]):
            class Meta:
                entity = UserDTO
                collection = cl

                # We use Access.PROTECTED to avoid clashes with naming
                method_access = Access.PROTECTED

            def get_by_username(self, username: str) -> UserDTO | None:
                # decorator adds protected method "_get"
                entity = self._get(username=username)
                return entity

            def create(self, entity: UserDTO) -> UserDTO:
                new_dto = self._add(entity=entity)
                return new_dto

        repo = MongoUserRepository()

        entity = UserDTO(username='admin', password='1234')
        new_user: UserDTO = repo.create(entity=entity)
        assert new_user.username == 'admin' and new_user.password == '1234'

        resolved_user: UserDTO = repo.get_by_username(username='admin')
        assert resolved_user.username == 'admin'


def test_decorator_with_protocol_and_dto_with_id():
    class IRepository(Protocol):
        def add(self, entity: EntityWithID) -> None:
            ...

        def get_by_id(self, id: str) -> EntityWithID | None:
            ...

    with in_collection(EntityWithID) as cl:
        @mongo_repository
        class MongoRepository:
            class Meta:
                entity = EntityWithID
                collection = cl
                method_access = Access.PROTECTED

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
