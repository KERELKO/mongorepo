# type: ignore
from dataclasses import dataclass, field
from typing import List

from mongorepo.decorators import mongo_repository
from mongorepo import Access

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

    updated_dto: ComplicatedDTO | None = repo.skills__append(value='c++', x='me')
    assert updated_dto is not None

    assert 'c++' in updated_dto.skills

    repo.skills__remove(value='python', x='me')

    dto: ComplicatedDTO | None = repo.get(x='me')
    assert dto is not None

    assert 'python' not in dto.skills

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
        types: list[str] | List[float] = field(default_factory=list)

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

    @mongo_repository(array_fields=['types'])
    class TestA4:
        class Meta:
            dto = A4
            collection = cl

    _ = TestA1()
    _ = TestA2()
    _ = TestA3()
    _ = TestA4()
    assert True
