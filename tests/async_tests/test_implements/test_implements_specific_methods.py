from typing import AsyncGenerator

from mongorepo import implements
from mongorepo.implements.methods import (
    AddBatchMethod,
    AddMethod,
    DecrementIntegerFieldMethod,
    DeleteMethod,
    GetAllMethod,
    GetListMethod,
    GetMethod,
    IncrementIntegerFieldMethod,
    ListAppendMethod,
    ListGetFieldValuesMethod,
    ListPopMethod,
    ListRemoveMethod,
    UpdateMethod,
)
from tests.common import (
    Box,
    MixDTO,
    NestedListDTO,
    SimpleDTO,
    in_async_collection,
)


async def test_implements_crud_with_specific_method_protocol():
    """Test `@implements` decorator with classes that implement
    `SpecificMethod` protocol."""

    async with in_async_collection(NestedListDTO) as c:
        class IRepo:
            async def get(self, title: str) -> NestedListDTO:
                ...

            async def add(self, model: NestedListDTO) -> NestedListDTO:
                ...

            async def update(self, model: NestedListDTO, title: str) -> NestedListDTO:
                ...

            async def delete(self, title: str) -> bool:
                ...

            async def add_batch(self, models: list[NestedListDTO]) -> None:
                ...

            async def get_all_by_title(self, title: str) -> AsyncGenerator[NestedListDTO, None]:
                ...

            async def get_model_list(
                self, title: str, limit: int, offset: int = 20,
            ) -> list[NestedListDTO]:
                ...

        @implements(
            IRepo,
            AddMethod(IRepo.add, dto='model'),
            GetMethod(IRepo.get, filters=['title']),
            UpdateMethod(IRepo.update, dto='model', filters=['title']),
            AddBatchMethod(IRepo.add_batch, dto_list='models'),
            GetAllMethod(IRepo.get_all_by_title, filters=['title']),
            GetListMethod(IRepo.get_model_list, offset='offset', limit='limit', filters=['title']),
            DeleteMethod(IRepo.delete, filters=['title']),
        )
        class MongoRepo:
            class Meta:
                collection = c
                dto = NestedListDTO

        r: IRepo = MongoRepo()  # type: ignore
        await r.add(NestedListDTO('...', dtos=[SimpleDTO(x='1', y=1), SimpleDTO(x='1', y=1)]))
        assert True

        dto = await r.get(title='...')
        assert dto is not None
        assert dto.title
        assert len(dto.dtos) == 2

        dto.title = 'Updated title'
        updated_dto = await r.update(model=dto, title='...')
        assert updated_dto.title == 'Updated title'

        await r.add_batch(
            [
                NestedListDTO(title='1', dtos=[SimpleDTO(x='1', y=1)]),
                NestedListDTO(title='2', dtos=[SimpleDTO(x='2', y=2)]),
            ],
        )

        async for dto in r.get_all_by_title(title='1'):
            assert dto.title == '1'

        dto_list = await r.get_model_list(title='2', limit=5, offset=0)
        assert len(dto_list) == 1
        assert dto_list[0].title == '2'

        deleted = await r.delete(title='1')
        assert deleted is True

        none = await r.get(title='1')
        assert none is None


async def test_implements_list_methods_with_specific_method_protocol():

    class IRepo:
        async def add(self, dto: NestedListDTO) -> None:
            ...

        # Change order of offset and remove its default value
        async def get_simple_dto_list_by_title(
            self, offset: int, title: str, limit: int = 20,
        ) -> list[SimpleDTO]:
            ...

        async def pop_dto_by_title(self, title: str) -> SimpleDTO:
            ...

        # Set dto as a second parameter
        async def append_dto_by_title(self, title: str, dto: SimpleDTO) -> None:
            ...

        async def remove_dto_by_title(self, dto: SimpleDTO, title: str) -> None:
            ...

    async with in_async_collection(NestedListDTO) as c:

        @implements(
            IRepo,
            AddMethod(IRepo.add, dto='dto'),
            ListGetFieldValuesMethod(
                source=IRepo.get_simple_dto_list_by_title, field_name='dtos',
                offset='offset',
                filters=['title'],
                limit='limit',
            ),
            ListPopMethod(IRepo.pop_dto_by_title, 'dtos', filters=['title']),
            ListAppendMethod(IRepo.append_dto_by_title, 'dtos', value='dto', filters=['title']),
            ListRemoveMethod(IRepo.remove_dto_by_title, 'dtos', value='dto', filters=['title']),
        )
        class MongoRepo:
            class Meta:
                collection = c
                dto = NestedListDTO

        r: IRepo = MongoRepo()  # type: ignore
        title = '...'
        await r.add(NestedListDTO(title, dtos=[SimpleDTO(x='1', y=1), SimpleDTO(x='1', y=1)]))

        # All arguments are keywords arguments
        _ = await r.get_simple_dto_list_by_title(offset=0, title=title, limit=20)
        # All arguments are keywords arguments + parameter by default
        _ = await r.get_simple_dto_list_by_title(offset=0, title=title)
        # All arguments are keyword arguments + random order
        _ = await r.get_simple_dto_list_by_title(limit=5, title=title, offset=1)

        await r.append_dto_by_title(title=title, dto=SimpleDTO(x='3', y=3))
        await r.append_dto_by_title(title, SimpleDTO(x='2', y=2))
        await r.append_dto_by_title(dto=SimpleDTO(x='2', y=2), title=title)

        _ = await r.pop_dto_by_title(title)
        _ = await r.pop_dto_by_title(title=title)

        await r.remove_dto_by_title(title=title, dto=SimpleDTO(x='1', y=1))
        await r.remove_dto_by_title(SimpleDTO(x='1', y=3), title)
        await r.remove_dto_by_title(SimpleDTO(x='1', y=1), title=title)

        assert True


async def test_implements_integer_methods_with_specific_method_protocol() -> None:
    class IRepo:
        async def get(self, id: str) -> MixDTO | None:
            ...

        async def add(self, dto: MixDTO) -> None:
            ...

        async def update_year_with_weight(self, id: str, weight: int) -> None:
            ...

        async def update_year(self, id: str) -> None:
            ...

    async with in_async_collection(MixDTO) as coll:
        @implements(
            IRepo,
            AddMethod(IRepo.add, dto='dto'),
            GetMethod(IRepo.get, filters=['id']),
            IncrementIntegerFieldMethod(
                IRepo.update_year_with_weight, field_name='year', filters=['id'], weight='weight',
            ),
            DecrementIntegerFieldMethod(
                IRepo.update_year, field_name='year', filters=['id'],
            ),
        )
        class MongoRepo:
            class Meta:
                dto = MixDTO
                collection = coll

    repo: IRepo = MongoRepo()  # type: ignore
    dto = MixDTO(
        id='1',
        name='box',
        year=2025,
        main_box=Box('box_1', 'toy'),
        records=[1, 2, 3],
        boxs=[Box('box_list_1', 'car'), Box('box_list_2', 'table')],
    )
    await repo.add(dto=dto)

    await repo.update_year_with_weight(id='1', weight=5)

    updated_dto = await repo.get(id='1')
    assert updated_dto is not None
    assert updated_dto.year == 2030

    await repo.update_year(id='1')

    updated_dto = await repo.get(id='1')
    assert updated_dto is not None
    assert updated_dto.year == 2029
