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
    c = custom_collection(NestedListDTO)

    class Repo(BaseMongoRepository[NestedDTO]):
        class Meta:
            collection = c

    _title = '#0000'

    new_dto = NestedDTO(title=_title, simple=SimpleDTO(x='x', y=1))

    repo = Repo()
    repo.add(new_dto)

    dto: NestedDTO | None = repo.get(title=_title)
    assert dto is not None
    assert dto.title == _title

    assert dto.simple.x == 'x'

    c.drop()


@pytest.mark.skip
def test_methods_with_nested_list_dto() -> None:
    c = custom_collection(NestedListDTO)

    class Repo(BaseMongoRepository[NestedListDTO]):
        class Meta:
            collection = c

    _title = '#8999'

    new_dto = NestedListDTO(title=_title, dtos=[SimpleDTO(x='x', y=1)])

    repo = Repo()
    repo.add(new_dto)

    dto: NestedListDTO | None = repo.get(title=_title)
    assert dto is not None
    assert dto.title == _title

    assert len(dto.dtos) == 1

    assert dto.dtos[0].x == 'x' and dto.dtos[0].y == 1

    c.drop()


def test_methods_with_dict_dto() -> None:
    c = custom_collection(DictDTO)

    class Repo(BaseMongoRepository[DictDTO]):
        class Meta:
            collection = c

    record_data = 'Read "Berserk again"'

    new_dto = DictDTO(
        oid='834yc948yh',
        records={'2019-12-02': 'Read "Berserk"', '2024-08-28': record_data},
    )

    repo = Repo()
    repo.add(new_dto)

    dto: DictDTO | None = repo.get(oid=new_dto.oid)
    assert dto is not None

    assert isinstance(dto.records, dict)

    assert dto.records['2024-08-28'] == record_data

    c.drop()
