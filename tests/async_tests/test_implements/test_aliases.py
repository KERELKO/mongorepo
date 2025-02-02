from mongorepo import implements
from mongorepo.implements.methods import AddMethod
from mongorepo.implements.methods import FieldAlias as FA
from mongorepo.implements.methods import GetMethod
from tests.common import NestedListDTO, SimpleDTO, in_async_collection


async def test_implements_crud_with_specific_method_protocol():
    """Test `@implements` decorator with classes that implement
    `SpecificMethod` protocol."""

    async with in_async_collection(NestedListDTO) as c:
        class IRepo:
            async def get(self, dto_title: str) -> NestedListDTO:
                ...

            async def add(self, model: NestedListDTO) -> NestedListDTO:
                ...

        @implements(
            IRepo,
            GetMethod(IRepo.get, filters=[FA('title', 'dto_title')]),
            AddMethod(IRepo.add, dto='model'),
        )
        class MongoRepo:
            class Meta:
                collection = c
                dto = NestedListDTO

        r: IRepo = MongoRepo()  # type: ignore
        await r.add(NestedListDTO('...', dtos=[SimpleDTO(x='1', y=1), SimpleDTO(x='1', y=1)]))

        dto = await r.get(dto_title='...')
        assert dto is not None
