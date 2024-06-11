# type: ignore
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

    assert hasattr(repo, 'append_to_skills') and hasattr(repo, 'remove_from_skills')

    repo.add(ComplicatedDTO(x='me', skills=['python', 'java']))

    updated_dto: ComplicatedDTO | None = repo.append_to_skills(value='c++', x='me')
    assert updated_dto is not None

    assert 'c++' in updated_dto.skills

    repo.remove_from_skills(value='python', x='me')

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
    assert hasattr(r, '_append_to_skills')

    cl.drop()
