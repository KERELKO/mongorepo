# type: ignore
from mongorepo import async_repository
from tests.common import NestedListEntity, SimpleEntity, custom_collection


async def test_can_use_array_methods_with_dto_fields() -> None:
    c = custom_collection(entity=NestedListEntity, async_client=True)

    @async_repository(list_fields=['dtos'])
    class MongoRepository:
        class Meta:
            entity = NestedListEntity
            collection = c

    repo = MongoRepository()

    await repo.add(
        NestedListEntity(
            title='Test',
            dtos=[
                SimpleEntity(x='1', y=1),
                SimpleEntity(x='2', y=2),
                SimpleEntity(x='3', y=3),
                SimpleEntity(x='4', y=4),
                SimpleEntity(x='5', y=5),
            ],
        ),
    )

    dtos = await repo.dtos__list(title='Test', offset=0, limit=10)
    assert dtos

    assert len(dtos) == 5

    assert dtos[0].x == '1'

    dto_slice = await repo.dtos__list(title='Test', offset=2, limit=4)

    assert dto_slice

    assert dto_slice[0].x == '3'

    last: SimpleEntity | None = await repo.dtos__pop(title='Test')
    assert last
    assert last.y == 5

    await repo.dtos__append(title='Test', value=SimpleEntity(x='10', y=10))

    the_latest_dto = await repo.dtos__pop(title='Test')
    assert the_latest_dto is not None

    assert the_latest_dto.x == '10' and the_latest_dto.y == 10
    await repo.dtos__remove(title='Test', value=SimpleEntity(x='4', y=4))

    entity: NestedListEntity | None = await repo.get(title='Test')
    assert entity
    for simple_dto in entity.dtos:
        assert simple_dto.x != '4' and simple_dto.y != 4

    c.drop()
