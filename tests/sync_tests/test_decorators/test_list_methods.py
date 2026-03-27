# type: ignore
from dataclasses import dataclass, field
from typing import List

from mongorepo import Access
from mongorepo.decorators import mongo_repository
from tests.common import (
    MultiFieldEntity,
    NestedListEntity,
    SimpleEntity,
    custom_collection,
    in_collection,
)


def test_can_push_and_pull_elements_from_list_with_decorator():

    with in_collection(MultiFieldEntity) as cl:
        @mongo_repository(list_fields=['skills'])
        class Repository:
            class Meta:
                entity = MultiFieldEntity
                collection = cl

        repo = Repository()

        assert hasattr(repo, 'skills__append') and hasattr(repo, 'skills__remove')

        repo.add(MultiFieldEntity(x='me', skills=['python', 'java']))

        repo.skills__append(value='c++', x='me')

        repo.skills__remove(value='python', x='me')

        entity: MultiFieldEntity | None = repo.get(x='me')
        assert entity is not None

        assert 'python' not in entity.skills
        assert 'c++' in entity.skills


def test_can_mix_methods_with_decorators():

    with in_collection(MultiFieldEntity) as cl:
        @mongo_repository(list_fields=['skills'], method_access=Access.PROTECTED)
        @mongo_repository
        class TestMongoRepository:
            class Meta:
                entity = MultiFieldEntity
                collection = cl

        r = TestMongoRepository()

        assert hasattr(r, 'get')
        assert hasattr(r, '_skills__remove')


def test_pop_method_with_decorator():

    with in_collection(MultiFieldEntity) as cl:
        @mongo_repository(list_fields=['skills'])
        class TestMongoRepository:
            class Meta:
                entity = MultiFieldEntity
                collection = cl

        r = TestMongoRepository()
        assert hasattr(r, 'skills__pop')
        r.add(MultiFieldEntity(x='List', skills=['java', 'c#', 'lua', 'c++', 'c']))

        r.skills__pop(x='List')

        entity = r.get(x='List')

        assert 'c' not in entity.skills

        cpp = r.skills__pop(x='List')

        assert cpp == 'c++'


def test_list_with_different_type_hints_decorator():

    @dataclass
    class A1:
        types: list[int]

    @dataclass
    class A2:
        types: list = field(default_factory=list)

    @dataclass
    class A3:
        types: List[float]

    @dataclass
    class A4:
        types: list[int | None]

    cl = custom_collection(A1)

    @mongo_repository(list_fields=['types'])
    class TestA1:
        class Meta:
            entity = A1
            collection = cl


    @mongo_repository(list_fields=['types'])
    class TestA2:
        class Meta:
            entity = A2
            collection = cl

    @mongo_repository(list_fields=['types'])
    class TestA3:
        class Meta:
            entity = A3
            collection = cl

    _ = TestA1()
    _ = TestA2()
    _ = TestA3()

    @mongo_repository(list_fields=['types'])
    class TestA4:
        class Meta:
            entity = A4
            collection = cl

    _ = TestA4

    cl.drop()
    assert True


def test_can_get_list_of_dto_field_values() -> None:
    c = custom_collection(NestedListEntity)

    @mongo_repository(list_fields=['dtos'])
    class MongoRepository:
        class Meta:
            entity = NestedListEntity
            collection = c

    repo = MongoRepository()

    repo.add(
        NestedListEntity(
            title='Test',
            dtos=[
                SimpleEntity(x='1', y=1),
                SimpleEntity(x='2', y=2),
                SimpleEntity(x='3', y=3),
                SimpleEntity(x='4', y=4),
                SimpleEntity(x='5', y=5),
            ],
        ),
    )

    dtos = repo.dtos__list(title='Test', offset=0, limit=10)
    assert dtos

    assert len(dtos) == 5

    assert dtos[0].x == '1'

    dto_slice = repo.dtos__list(title='Test', offset=2, limit=4)

    assert dto_slice

    assert dto_slice[0].x == '3'

    last: SimpleEntity | None = repo.dtos__pop(title='Test')
    assert last
    assert last.y == 5

    c.drop()
