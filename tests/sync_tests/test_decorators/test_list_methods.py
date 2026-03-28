# type: ignore
from dataclasses import dataclass, field
from typing import List

from mongorepo import MethodAccess, RepositoryConfig, repository
from tests.common import (
    MultiFieldEntity,
    NestedListEntity,
    SimpleEntity,
    in_collection,
)


def test_can_push_and_pull_elements_from_list_with_decorator():

    with in_collection(MultiFieldEntity) as cl:
        @repository(list_fields=['skills'], config=RepositoryConfig(entity_type=MultiFieldEntity, collection=cl))
        class Repository:
            ...

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
        @repository(
            list_fields=['skills'],
            config=RepositoryConfig(entity_type=MultiFieldEntity, collection=cl, method_access=MethodAccess.PROTECTED),
        )
        @repository(config=RepositoryConfig(entity_type=MultiFieldEntity, collection=cl))
        class TestMongoRepository:
            ...

        r = TestMongoRepository()

        assert hasattr(r, 'get')
        assert hasattr(r, '_skills__remove')


def test_pop_method_with_decorator():

    with in_collection(MultiFieldEntity) as cl:
        @repository(list_fields=['skills'], config=RepositoryConfig(entity_type=MultiFieldEntity, collection=cl))
        class TestMongoRepository:
            ...

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

    with in_collection(A1) as cl:
        config = RepositoryConfig(entity_type=A1, collection=cl)

        @repository(list_fields=['types'], config=config)
        class TestA1:
            ...

        @repository(list_fields=['types'], config=config)
        class TestA2:
            ...

        @repository(list_fields=['types'], config=config)
        class TestA3:
            ...

        _ = TestA1()
        _ = TestA2()
        _ = TestA3()

        @repository(list_fields=['types'], config=config)
        class TestA4:
            ...

        _ = TestA4

    assert True


def test_can_get_list_of_dto_field_values() -> None:

    with in_collection(NestedListEntity) as cl:
        @repository(list_fields=['dtos'], config=RepositoryConfig(entity_type=NestedListEntity, collection=cl))
        class MongoRepository:
            ...

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
