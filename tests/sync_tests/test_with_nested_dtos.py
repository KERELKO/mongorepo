import pytest

from tests.common import (  # noqa
    NestedDTO,
    NestedListDTO,
    SimpleDTO,
    DictDTO,
    custom_collection,
)
from mongorepo.classes import BaseMongoRepository


def test_methods_with_nested_dto() -> None:
    class Repo(BaseMongoRepository[NestedDTO]):
        class Meta:
            collection = custom_collection(NestedDTO)

    new_dto = NestedDTO(title='ho ho ho', simple=SimpleDTO(x='x', y=1))

    repo = Repo()
    repo.add(new_dto)

    dto: NestedDTO | None = repo.get(title='ho ho ho')
    assert dto is not None
    assert dto.title == 'ho ho ho'

    assert dto.simple.x == 'x'


@pytest.mark.skip
def test_methods_with_nested_list_dto() -> None:
    class Repo(BaseMongoRepository[NestedListDTO]):
        class Meta:
            collection = custom_collection(NestedListDTO)

    new_dto = NestedListDTO(title='NestedListDTO', dtos=[SimpleDTO(x='x', y=1)])

    repo = Repo()
    repo.add(new_dto)

    dto: NestedListDTO | None = repo.get(title='NestedListDTO')
    assert dto is not None
    assert dto.title == 'NestedListDTO'

    assert len(dto.dtos) == 1

    assert dto.dtos[0].x == 'x' and dto.dtos[0].y == 1


def test_methods_with_dict_dto() -> None:
    class Repo(BaseMongoRepository[DictDTO]):
        class Meta:
            collection = custom_collection(DictDTO)

    new_dto = DictDTO(
        oid='834yc948yh',
        records={'2019-12-02': 'Read "Berserk"', '2024-08-28': 'Read "Berserk again"'},
    )

    repo = Repo()
    repo.add(new_dto)

    dto: DictDTO | None = repo.get(oid=new_dto.oid)
    assert dto is not None

    assert isinstance(dto.records, dict)

    assert dto.records['2024-08-28'] == 'Read "Berserk again"'
