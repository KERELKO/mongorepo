# type: ignore
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Protocol

from mongorepo import DTO, Access
from mongorepo.classes import BaseMongoRepository
from mongorepo.decorators import mongo_repository
from tests.common import DTOWithID, collection_for_dto_with_id, mongo_client


def test_decorator_with_abstract_class():
    # Suppose we have abstract repository in our architecture
    # but mongo_repository's methods does not fit to it
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

    cl = mongo_client()['users_db']['users']

    # Solution
    @mongo_repository
    class MongoUserRepository(AbstractUserRepository[UserDTO]):
        class Meta:
            dto = UserDTO
            collection = cl

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

    cl.drop()


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

    # NOTE: In this example we can use @abstractmethod
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
                raise NoProductAvailable
            return product

    collection = mongo_client()['product_db']['product']
    repo = MongoProductRepository(collection=collection)

    product = Product(title='phone', price=499, description='the best phone')
    repo.add(dto=product)

    resolved_product: Product = repo.get(title='phone', price=499)

    assert resolved_product.title == 'phone' and product.price == 499
    assert resolved_product.description == 'the best phone'

    collection.drop()


def test_decorator_with_protocol_and_dto_with_id():
    class IRepository(Protocol):
        def add(self, dto: DTOWithID) -> None:
            ...

        def get_by_id(self, id: str) -> DTOWithID | None:
            ...

    cl = collection_for_dto_with_id()

    @mongo_repository
    class MongoRepository:
        class Meta:
            dto = DTOWithID
            collection = cl
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
    resolved_dto: DTOWithID | None = repo.get_by_id(id=dto_id)
    assert resolved_dto is not None
    assert resolved_dto.y == 10

    assert resolved_dto._id == dto_id

    cl.drop()
