# type: ignore
from mongorepo import async_repository
from tests.common import SimpleEntity, in_async_collection


async def test_can_increment_and_decrement_field_with_decorator():

    async with in_async_collection(SimpleEntity) as cl:

        @async_repository(integer_fields=['y'])
        class Repository:
            class Meta:
                entity = SimpleEntity
                collection = cl

        repo = Repository()

        await repo.add(SimpleEntity(x='admin', y=10))

        await repo.incr__y(x='admin')
        await repo.incr__y(x='admin')
        await repo.incr__y(x='admin')
        await repo.incr__y(x='admin')

        await repo.decr__y(x='admin')

        entity = await repo.get(x='admin')
        assert entity.y == 13
