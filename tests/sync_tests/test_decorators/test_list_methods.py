# type: ignore
from dataclasses import dataclass, field
from typing import List

import pytest

from mongorepo.decorators import mongo_repository
from mongorepo import Access
from mongorepo import exceptions

from tests.common import NestedListDTO, custom_collection, SimpleDTO
from tests.common import ComplicatedDTO, collection_for_complicated_dto


def test_can_push_and_pull_elements_from_list_with_decorator():
    cl = collection_for_complicated_dto()

    @mongo_repository(array_fields=['skills'])
    class Repository:
        class Meta:
            dto = ComplicatedDTO
            collection = cl

    repo = Repository()

    assert hasattr(repo, 'skills__append') and hasattr(repo, 'skills__remove')

    repo.add(ComplicatedDTO(x='me', skills=['python', 'java']))

    repo.skills__append(value='c++', x='me')

    repo.skills__remove(value='python', x='me')

    dto: ComplicatedDTO | None = repo.get(x='me')
    assert dto is not None

    assert 'python' not in dto.skills
    assert 'c++' in dto.skills

    cl.drop()


def test_can_mix_methods_with_decorators():
    cl = collection_for_complicated_dto()

    @mongo_repository(array_fields=['skills'], method_access=Access.PROTECTED)
    @mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = ComplicatedDTO
            collection = cl

    r = TestMongoRepository()

    assert hasattr(r, 'get')
    assert hasattr(r, '_skills__remove')

    cl.drop()


def test_pop_method_with_decorator():
    cl = collection_for_complicated_dto()

    @mongo_repository(array_fields=['skills'])
    class TestMongoRepository:
        class Meta:
            dto = ComplicatedDTO
            collection = cl

    r = TestMongoRepository()
    assert hasattr(r, 'skills__pop')
    r.add(ComplicatedDTO(x='List', skills=['java', 'c#', 'lua', 'c++', 'c']))

    r.skills__pop(x='List')

    dto = r.get(x='List')

    assert 'c' not in dto.skills

    cpp = r.skills__pop(x='List')

    assert cpp == 'c++'

    cl.drop()


def test_list_with_different_type_hints_decorator():
    cl = collection_for_complicated_dto()

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

    @mongo_repository(array_fields=['types'])
    class TestA1:
        class Meta:
            dto = A1
            collection = cl

    @mongo_repository(array_fields=['types'])
    class TestA2:
        class Meta:
            dto = A2
            collection = cl

    @mongo_repository(array_fields=['types'])
    class TestA3:
        class Meta:
            dto = A3
            collection = cl

    _ = TestA1()
    _ = TestA2()
    _ = TestA3()

    with pytest.raises(exceptions.TypeHintException):
        @mongo_repository(array_fields=['types'])
        class TestA4:
            class Meta:
                dto = A4
                collection = cl

        _ = TestA4

    assert True


def test_can_get_list_of_dto_field_values() -> None:
    c = custom_collection(dto=NestedListDTO)

    @mongo_repository(array_fields=['dtos'])
    class MongoRepository:
        class Meta:
            dto = NestedListDTO
            collection = c

    repo = MongoRepository()

    repo.add(
        NestedListDTO(
            title='Test',
            dtos=[
                SimpleDTO(x='1', y=1),
                SimpleDTO(x='2', y=2),
                SimpleDTO(x='3', y=3),
                SimpleDTO(x='4', y=4),
                SimpleDTO(x='5', y=5),
            ]
        )
    )

    dtos = repo.get_dtos_list(title='Test', offset=0, limit=10)
    assert dtos

    assert len(dtos) == 5

    assert dtos[0].x == '1'

    dto_slice = repo.get_dtos_list(title='Test', offset=2, limit=4)

    assert dto_slice

    assert dto_slice[0].x == '3'

    c.drop()
