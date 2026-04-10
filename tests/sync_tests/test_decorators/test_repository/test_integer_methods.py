# mypy: disable-error-code="attr-defined"
from mongorepo import RepositoryConfig, repository
from tests.common import SimpleEntity, in_collection


def test_can_increment_and_decrement_field_with_decorator() -> None:

    with in_collection(SimpleEntity) as coll:
        @repository(integer_fields=['y'], config=RepositoryConfig(entity_type=SimpleEntity, collection=coll))
        class Repository:
            ...

        repo = Repository()

        repo.add(SimpleEntity(x='admin', y=10))

        repo.incr__y(x='admin')
        repo.incr__y(x='admin')
        repo.incr__y(x='admin')
        repo.incr__y(x='admin')

        repo.decr__y(x='admin')

        entity = repo.get(x='admin')
        assert entity.y == 13
