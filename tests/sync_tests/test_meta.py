# type: ignore
from dataclasses import dataclass

from mongorepo.decorators import mongo_repository
from tests.common import mongo_client


def test_repo_does_not_include_id_in_dto():
    """Test without `id_field` in Meta class"""

    @dataclass
    class WithoutId:
        name: str = ''

    @mongo_repository
    class WithoutIdRepository:
        class Meta:
            dto = WithoutId
            collection = mongo_client()['test_id_field_db']['withoutid']

    r_2 = WithoutIdRepository()
    r_2.add(WithoutId(name='larry'))
    without_id_dto = r_2.get(name='larry')

    assert not hasattr(without_id_dto, 'oid')
    assert not hasattr(without_id_dto, '_id')
    assert not hasattr(without_id_dto, 'id')


def test_repo_include_id_in_dto():
    """Test with `id_field` in Meta class"""

    @dataclass
    class WithId:
        oid: str = ''
        name: str = ''

    @mongo_repository
    class WithIdRepository:
        class Meta:
            # set mongodb oid to dto field specified in "id_field"
            id_field = 'oid'
            dto = WithId
            collection = mongo_client()['test_id_field_db']['withid']

    r_1 = WithIdRepository()
    inserted_dto = r_1.add(WithId(name='cookie'))
    assert len(inserted_dto.oid) >= 24, inserted_dto.oid
    with_id_dto = r_1.get(name='cookie')

    assert with_id_dto.oid, with_id_dto.oid

    dto = r_1.get(oid=inserted_dto.oid)
    assert dto is not None
    assert dto.name == 'cookie'
