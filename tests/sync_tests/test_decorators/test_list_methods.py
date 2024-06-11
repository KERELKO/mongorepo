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
