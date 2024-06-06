# type: ignore
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Protocol

import pytest

from tests.common import (
    DTOWithID,
    ComplicatedDTO,
    collection_for_dto_with_id,
    collection_for_complicated_dto,
)

from mongorepo.base import DTO, Access
from mongorepo.decorators import mongo_repository_factory
from mongorepo.classes import BaseMongoRepository

from conf import mongo_client


def test_decorator_with_abstract_class():
    # Suppose we have abstract repository in our architecture
    # but mongo_repository_factory's methods does not fit to it
    # there is the simplest way to fix it

    # NOTE: we can't use @abstractmethod because it's will raise an error
    # you can still use typing.Protocol, tho
    class AbstractUserRepository(Generic[DTO], ABC):
        def get_by_username(self, username: str) -> DTO | None:
            raise NotImplementedError

        def create(self, dto: DTO) -> DTO:
            raise NotImplementedError

    @dataclass
    class UserDTO:
        username: str
        password: str

    # Solution
    @mongo_repository_factory
    class MongoUserRepository(AbstractUserRepository[UserDTO]):
        class Meta:
            dto = UserDTO
            collection = mongo_client()['users_db']['users']

            # We use Access.PROTECTED to avoid clashes with naming
            method_access = Access.PROTECTED

        def get_by_username(self, username: str) -> UserDTO | None:
            # decorator adds protected method "_get"
            dto = self._get(username=username)
            return dto

        def create(self, dto: UserDTO) -> UserDTO:
            new_dto = self._add(dto=dto)
            return new_dto

    repo = MongoUserRepository()

    dto = UserDTO(username='admin', password='1234')
    new_user: UserDTO = repo.create(dto=dto)
    assert new_user.username == 'admin' and new_user.password == '1234'

    resolved_user: UserDTO = repo.get_by_username(username='admin')
    assert resolved_user.username == 'admin'


def test_base_mongo_class_with_abstract_class():
    # And again we have abstract repository in our architecture like in the previous problem
    # but BaseMongoRepository's methods does not fit to it
    # I'll show you the simplest way to fix it

    @dataclass
    class Product:
        title: str
        price: int
        description: str = ''

    class NoProductAvailable(Exception):
        ...

    # NOTE: In this example we can use @abstractmethod because
    # abstract class methods have the same naming as our base repository methods
    class AbstractRepository(Generic[DTO], ABC):
        @abstractmethod
        def add(self, dto: DTO) -> DTO:
            ...

        @abstractmethod
        def get(self, title: str, price: int) -> DTO:
            ...

    class MongoProductRepository(BaseMongoRepository[Product], AbstractRepository[Product]):
        def add(self, dto: Product) -> Product:
            # use super() to call parent method
            new_dto: Product = super().add(dto=dto)
            return new_dto

        def get(self, title: str, price: int) -> Product:
            product: Product | None = super().get(title=title, price=price)
            if not product:
                raise NoProductAvailable()
            return product

    collection = mongo_client()['product_db']['product']
    repo = MongoProductRepository(collection=collection, index='price')

    product = Product(title='phone', price=499, description='the best phone')
    repo.add(dto=product)

    resolved_product: Product = repo.get(title='phone', price=499)

    assert resolved_product.title == 'phone' and product.price == 499
    assert resolved_product.description == 'the best phone'


def test_decorator_with_protocol_and_dto_with_id():
    class IRepository(Protocol):
        def add(self, dto: DTOWithID) -> None:
            ...

        def get_by_id(self, id: str) -> DTOWithID | None:
            ...

    @mongo_repository_factory
    class MongoRepository:
        class Meta:
            dto = DTOWithID
            collection = collection_for_dto_with_id()
            method_access = Access.PROTECTED

        def get_by_id(self, id: str) -> DTOWithID | None:
            dto = self._get(_id=id)
            return dto

        def add(self, dto: DTOWithID) -> None:
            self._add(dto=dto)

    repo = MongoRepository()
    dto = DTOWithID(x='one two', y=10)
    dto_id: str = dto._id
    repo.add(dto)

    # get dto with generated id
    resolved_dto = repo.get_by_id(id=dto_id)
    assert resolved_dto is not None
    assert resolved_dto.y == 10

    assert resolved_dto._id == dto_id


@pytest.mark.skip(reason='Not implemented yet')
def test_can_replace_methods_with_parent_class_methods():
    # Idea: to dinamically replace methods of mongo repo class with parent class methods

    class BaseRepository(Generic[DTO]):
        def get_by_x(self, x: str) -> DTO | None:
            ...

        def create(self, dto: DTO) -> DTO:
            ...

        def get_list(self, offset: int = 0, limit: int = 20) -> list[DTO]:
            ...

        def delete_by_id(self, id: str) -> DTO:
            ...

    class MongoRepository(BaseMongoRepository[ComplicatedDTO], BaseRepository[ComplicatedDTO]):
        class Meta:
            parent_methods: dict[str, str] = {
                'get': 'get_by_x',
                'add': 'create',
                'get_all': 'get_list',
                'delete': 'delete_by_id',
            }

    repo = MongoRepository(collection_for_complicated_dto())
    dto = ComplicatedDTO(x='x')
    repo.create(dto=dto)

    dto_x = repo.get_by_x(x=dto.x)
    assert dto_x is not None

    for dto in repo.get_list(offset=0, limit=2):
        assert isinstance(dto, ComplicatedDTO)

    deleted_dto = repo.delete_by_x(x=dto_x.x)
    assert deleted_dto is not None
