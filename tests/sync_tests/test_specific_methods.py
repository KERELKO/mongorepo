# type: ignore
from mongorepo.decorators import mongo_repository
from tests.common import (
    ComplicatedDTO,
    collection_for_complicated_dto,
    SimpleDTO,
    collection_for_simple_dto,
)


def test_can_increment_and_decrement_field_with_decorator():
    cl = collection_for_simple_dto()

    @mongo_repository(integer_fields=['y'])
    class Repository:
        class Meta:
            dto = SimpleDTO
            collection = cl

    repo = Repository()

    repo.add(SimpleDTO(x='admin', y=10))

    repo.increment_y(x='admin')
    repo.increment_y(x='admin')
    repo.increment_y(x='admin')
    repo.increment_y(x='admin')

    repo.decrement_y(x='admin')

    dto = repo.get(x='admin')
    assert dto.y == 13

    dto = repo.increment_y(x='admin')
    assert dto.y == 14

    cl.drop()


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
