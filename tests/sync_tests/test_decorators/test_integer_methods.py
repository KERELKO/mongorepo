# type: ignore
from mongorepo.decorators import mongo_repository
from tests.common import (
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

    repo.incr__y(x='admin')
    repo.incr__y(x='admin')
    repo.incr__y(x='admin')
    repo.incr__y(x='admin')

    repo.decr__y(x='admin')

    dto = repo.get(x='admin')
    assert dto.y == 13

    cl.drop()
