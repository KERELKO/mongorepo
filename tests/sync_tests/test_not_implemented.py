# type: ignore
from abc import ABC
from typing import Generic, TypeVar

from mongorepo.decorators import mongo_repository
from mongorepo._implements_deco.handler import implements
from mongorepo import DTO
from tests.common import (
    ComplicatedDTO,
    SimpleDTO,
    collection_for_complicated_dto,
    collection_for_simple_dto
)


def test_can_substitute_get_method():
    T = TypeVar('T')

    class A(Generic[T], ABC):
        def get_by_x(self, x: str) -> T:
            raise NotImplementedError

    @implements(A)
    @mongo_repository(get=False, get_all=False, get_list=False, delete=False, update=False)
    class Repository:
        class Meta:
            dto = SimpleDTO
            collection = collection_for_simple_dto()
            substitute = {'get': 'get_by_x'}

    r = Repository()
    assert hasattr(r, 'get_by_x')
    r.add(SimpleDTO(x='123', y=123))

    dto: SimpleDTO | None = r.get_by_x(x='123')
    assert dto is not None
    assert dto.x == '123'

    dto: SimpleDTO | None = r.get_by_x('123')
    assert dto is not None
    assert dto.x == '123'

    assert r.get_by_x.__annotations__['return'] == SimpleDTO


def test_can_substitute_methods_with_decorator():
    # Idea: to dynamically replace methods of mongo repo class with other class methods

    class BaseRepository(Generic[DTO], ABC):
        def get_by_name(self, name: str) -> DTO | None:
            raise NotImplementedError

        def create(self, entity: DTO) -> DTO:
            raise NotImplementedError

    @implements(BaseRepository)
    class SubstitudeWithDecorator:
        class Meta:
            dto = ComplicatedDTO
            # 'get' - mongorepo method, 'get_by_name' - method that must be implemented dynamically
            substitute = {'get': 'get_by_name', 'add': 'create'}
            collection = collection_for_complicated_dto()

    repo_dec = SubstitudeWithDecorator()

    assert hasattr(repo_dec, 'create')
    assert hasattr(repo_dec, 'get_by_name')

    entity = ComplicatedDTO(x='test', name='admin', y=True, skills=['python'])
    repo_dec.create(entity=entity)

    record: ComplicatedDTO | None = repo_dec.get_by_name(name='admin')  # type: ignore

    assert record is not None
    assert record.name == 'admin'
    assert record.y is True
    assert record.skills == ['python']
