# type: ignore
from mongorepo.decorators import mongo_repository
from tests.common import SimpleEntity, in_collection


def test_can_increment_and_decrement_field_with_decorator():

    with in_collection(SimpleEntity) as coll:
        @mongo_repository(integer_fields=['y'])
        class Repository:
            class Meta:
                entity = SimpleEntity
                collection = coll

        repo = Repository()

        repo.add(SimpleEntity(x='admin', y=10))

        repo.incr__y(x='admin')
        repo.incr__y(x='admin')
        repo.incr__y(x='admin')
        repo.incr__y(x='admin')

        repo.decr__y(x='admin')

        entity = repo.get(x='admin')
        assert entity.y == 13
