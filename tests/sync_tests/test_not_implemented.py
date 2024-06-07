# type: ignore
from typing import Generic

import pytest

from mongorepo.base import DTO
from mongorepo.classes import BaseMongoRepository
from mongorepo.decorators import mongo_repository
from mongorepo.exceptions import NoDTOTypeException

from tests.common import (  # type: ignore
    ComplicatedDTO,
    SimpleDTO,
    collection_for_complicated_dto,
    collection_for_simple_dto,
)


def test_can_access_dto_in_type_hints_decorator():
    cl = collection_for_simple_dto()

    @mongo_repository(delete=False)
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl

    repo = TestMongoRepository()

    assert hasattr(repo, 'add')
    assert not hasattr(repo, 'delete')


def test_can_access_dto_type_in_type_hints_class_repo():
    cl = collection_for_simple_dto()

    class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
        ...

    _ = TestMongoRepository(cl)


def test_cannot_access_dto_type_in_type_hints_decorator():
    with pytest.raises(NoDTOTypeException):

        @mongo_repository
        class TestMongoRepository:
            class Meta:
                ...


def test_cannot_access_dto_type_in_type_hints_class():
    with pytest.raises(NoDTOTypeException):
        class TestMongoRepository(BaseMongoRepository):
            ...

        _ = TestMongoRepository(collection=collection_for_simple_dto())


def test_cannot_access_dto_type_with_class_inheritance():
    with pytest.raises(NoDTOTypeException):
        class A(Generic[DTO]):
            ...

        class B(BaseMongoRepository, A):
            ...

        _ = B(collection=collection_for_simple_dto())


def test_move_collection_init_to_meta_in_class_repo():
    class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
        class Meta:
            collection = collection_for_simple_dto()

    repo = TestMongoRepository()
    assert hasattr(repo, 'add')


@pytest.mark.skip(reason='Not implemented yet')
def test_can_replace_methods_with_parent_class_methods():
    # Idea: to dynamically replace methods of mongo repo class with parent class methods

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
