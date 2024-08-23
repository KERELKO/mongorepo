# type: ignore
from mongorepo.asyncio.decorators import async_mongo_repository
from tests.common import NestedListDTO, custom_collection, SimpleDTO


async def test_can_get_list_of_dto_field_values() -> None:
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
            ]
        )
    )

    dtos = await repo.get_dtos_list(title='Test', offset=0, limit=10)
    assert dtos

    assert len(dtos) == 5

    assert dtos[0].x == '1'

    dto_slice = await repo.get_dtos_list(title='Test', offset=2, limit=4)

    assert dto_slice

    assert dto_slice[0].x == '3'

    c.drop()
