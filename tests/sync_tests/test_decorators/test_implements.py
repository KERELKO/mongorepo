# type: ignore
from abc import ABC
from typing import Generic, Protocol, TypeVar

from mongorepo import DTO
from mongorepo.decorators import implements, mongo_repository
from tests.common import (
    ComplicatedDTO,
    SimpleDTO,
    collection_for_complicated_dto,
    collection_for_simple_dto,
)


def test_implements():
    c = collection_for_simple_dto()

    class A:
        def get_x(self, id: str) -> None:
            ...

    @implements(A, get=A.get_x)
    class B:
        class Meta:
            dto = SimpleDTO
            collection = c

    r = B()
    _ = r.get_x(id='123')
    _ = r.get_x('123')
    _ = r.get_x(id='123')


def test_can_substitute_get_method():
    c = collection_for_simple_dto()

    T = TypeVar('T')

    class A(Generic[T], ABC):
        def get_by_x(self, x: str) -> T:
            raise NotImplementedError

    @implements(A)
    @mongo_repository(get=False, get_all=False, get_list=False, delete=False, update=False)
    class Repository:
        class Meta:
            dto = SimpleDTO
            collection = c
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

    c.drop()


def test_crud_methods_with_implements_decorator():
    # Idea: to dynamically replace methods of mongorepo class with other class methods
    c = collection_for_complicated_dto()

    class BaseRepository(Generic[DTO], ABC):
        def get_by_name(self, name: str) -> DTO | None:
            raise NotImplementedError

        def create(self, entity: DTO) -> DTO:
            raise NotImplementedError

        def update_entity(self, entity: DTO, x: str) -> None:
            raise NotImplementedError

        def delete_by_name(self, name: str) -> None:
            raise NotImplementedError

    @implements(BaseRepository)
    class SubstitudeWithDecorator:
        class Meta:
            dto = ComplicatedDTO
            # 'get' - mongorepo method, 'get_by_name' - method that must be implemented dynamically
            substitute = {
                'get': 'get_by_name',
                'add': 'create',
                'update': 'update_entity',
                'delete': 'delete_by_name',
            }
            collection = c

    repo = SubstitudeWithDecorator()

    assert hasattr(repo, 'create')
    assert hasattr(repo, 'get_by_name')
    assert hasattr(repo, 'update_entity')
    assert hasattr(repo, 'delete_by_name')

    entity = ComplicatedDTO(x='test', name='admin', y=True, skills=['python'])
    repo.create(entity=entity)

    record: ComplicatedDTO | None = repo.get_by_name(name='admin')
    assert record is not None
    assert record.name == 'admin'
    assert record.y is True
    assert record.skills == ['python']

    updated_entity = repo.update_entity(
        entity=ComplicatedDTO(x='1', y=False, name='admin'),
        x='test',
    )
    assert updated_entity is not None
    assert updated_entity.y is False

    is_deleted = repo.delete_by_name(name='admin')
    assert is_deleted is True

    c.drop()


def test_can_pass_substitute_in_params():
    c = collection_for_complicated_dto()

    T = TypeVar('T')

    class IRepo(Protocol[T]):
        def make_new(self, obj: T) -> T | None:
            ...

        def get(self, x: str) -> T | None:
            ...

    @implements(IRepo, add=IRepo.make_new, get='get')
    class MyRepo:
        class Meta:
            dto = ComplicatedDTO
            collection = c

    r = MyRepo()
    assert hasattr(r, 'make_new')
    assert hasattr(r, 'get')

    r.make_new(obj=ComplicatedDTO(x='12'))

    dto = r.get(x='12')
    assert dto is not None

    c.drop()


def test_implements_with_different_parameters_types():
    c = collection_for_complicated_dto()

    T = TypeVar('T')

    class IRepo(Protocol[T]):
        def add(self, obj: T) -> T | None:
            ...

        def get(self, x: str, y: bool = True) -> T | None:
            ...

        def delete(self, y: bool) -> bool:
            ...

        def update(self, x: str, obj: T) -> T | None:
            ...

    @implements(IRepo, add=IRepo.add, get='get', delete=IRepo.delete, update=IRepo.update)
    class MyRepo:
        class Meta:
            dto = ComplicatedDTO
            collection = c

    r = MyRepo()
    assert hasattr(r, 'add')
    assert hasattr(r, 'get')
    assert hasattr(r, 'delete')
    assert hasattr(r, 'update')

    _ = r.add(obj=ComplicatedDTO(x='123'))
    _ = r.add(ComplicatedDTO('125'))

    _ = r.get(x='123', y=False)
    _ = r.get('123', False)
    _ = r.get(y=False, x='123')

    _ = r.update(x='123', obj=ComplicatedDTO('888'))
    _ = r.update('888', ComplicatedDTO('999'))

    _ = r.delete(True)
    _ = r.delete(y=True)

    assert True

    c.drop()
