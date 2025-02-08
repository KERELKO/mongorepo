# type: ignore
from mongorepo.asyncio.decorators import async_mongo_repository
from tests.common import NestedListDTO, SimpleDTO, custom_collection


async def test_can_use_array_methods_with_dto_fields() -> None:
    c = custom_collection(dto=NestedListDTO, async_client=True)

    @async_mongo_repository(array_fields=['dtos'])
    class MongoRepository:
        class Meta:
            dto = NestedListDTO
            collection = c

    repo = MongoRepository()

    await repo.add(
        NestedListDTO(
            title='Test',
            dtos=[
                SimpleDTO(x='1', y=1),
                SimpleDTO(x='2', y=2),
                SimpleDTO(x='3', y=3),
                SimpleDTO(x='4', y=4),
                SimpleDTO(x='5', y=5),
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

    last: SimpleDTO | None = await repo.dtos__pop(title='Test')
    assert last
    assert last.y == 5

    await repo.dtos__append(title='Test', value=SimpleDTO(x='10', y=10))

    the_latest_dto = await repo.dtos__pop(title='Test')
    assert the_latest_dto is not None

    assert the_latest_dto.x == '10' and the_latest_dto.y == 10
    await repo.dtos__remove(title='Test', value=SimpleDTO(x='4', y=4))

    dto: NestedListDTO | None = await repo.get(title='Test')
    assert dto
    for simple_dto in dto.dtos:
        assert simple_dto.x != '4' and simple_dto.y != 4

    c.drop()
