from mongorepo.decorators import implements
from tests.common import SimpleDTO, custom_collection


async def test_crud_with_implements() -> None:
    c = custom_collection(SimpleDTO.__name__, async_client=True)

    class BaseRepo:
        async def get_by_y(self, y: str) -> SimpleDTO | None:
            ...

        async def add(self, dto: SimpleDTO) -> SimpleDTO:
            ...

    @implements(BaseRepo, get=BaseRepo.get_by_y, add=BaseRepo.add)
    class MongoRepo:
        class Meta:
            dto = SimpleDTO
            collection = c

    repo = MongoRepo()

    await repo.add(SimpleDTO(x='10', y=10))  # type: ignore

    dto = await repo.get_by_y(y=10)  # type: ignore

    assert dto is not None

    assert dto.x == '10'

    c.drop()
