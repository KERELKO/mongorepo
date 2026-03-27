# type: ignore
from tests.common import NestedEntity, NestedListEntity, SimpleEntity, in_collection, DictEntity
from mongorepo.decorators import mongo_repository


def test_methods_with_nested_dto() -> None:

    with in_collection(NestedEntity) as c:
        @mongo_repository
        class Repo:
            class Meta:
                collection = c
                entity = NestedEntity

        _title = '#0000'

        new_dto = NestedEntity(title=_title, simple=SimpleEntity(x='x', y=1))

        repo = Repo()
        repo.add(new_dto)

        entity: NestedEntity | None = repo.get(title=_title)
        assert entity is not None
        assert entity.title == _title

        assert entity.simple.x == 'x'


def test_methods_with_nested_list_dto() -> None:

    with in_collection(NestedListEntity) as c:
        @mongo_repository
        class Repo:
            class Meta:
                collection = c
                entity = NestedListEntity

        _title = '#8999'

        new_dto = NestedListEntity(title=_title, dtos=[SimpleEntity(x='x', y=1)])

        repo = Repo()
        repo.add(new_dto)

        entity: NestedListEntity | None = repo.get(title=_title)
        assert entity is not None
        assert entity.title == _title

        assert len(entity.dtos) == 1

        assert entity.dtos[0].x == 'x' and entity.dtos[0].y == 1


def test_methods_with_dict_dto() -> None:

    with in_collection(DictEntity) as c:
        @mongo_repository
        class Repo:
            class Meta:
                collection = c
                entity = DictEntity

        record_data = 'Read "Berserk again"'

        new_dto = DictEntity(
            oid='834yc948yh',
            records={'2019-12-02': 'Read "Berserk"', '2024-08-28': record_data},
        )

        repo = Repo()
        repo.add(new_dto)

        entity: DictEntity | None = repo.get(oid=new_dto.oid)
        assert entity is not None

        assert isinstance(entity.records, dict)

        assert entity.records['2024-08-28'] == record_data
