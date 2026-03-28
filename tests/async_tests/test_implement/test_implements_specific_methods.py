# mypy: disable-error-code="empty-body"
from typing import AsyncGenerator

from mongorepo import RepositoryConfig
from mongorepo.implement import implement
from mongorepo.implement.methods import (
    AddBatchMethod,
    AddMethod,
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
    MixedEntity,
    NestedListEntity,
    SimpleEntity,
    in_async_collection,
)


async def test_implement_crud_with_specific_method_protocol():
    """Test `@implement` decorator with classes that implement `SpecificMethod`
    protocol."""

    class IRepo:
        async def get(self, title: str) -> NestedListEntity:
            ...

        async def add(self, model: NestedListEntity) -> NestedListEntity:
            ...

        async def update(self, model: NestedListEntity, title: str) -> NestedListEntity:
            ...

        async def delete(self, title: str) -> bool:
            ...

        async def add_batch(self, models: list[NestedListEntity]) -> None:
            ...

        async def get_all_by_title(self, title: str) -> AsyncGenerator[NestedListEntity, None]:
            ...

        async def get_model_list(
            self, title: str, limit: int, offset: int = 20,
        ) -> list[NestedListEntity]:
            ...

    async with in_async_collection(NestedListEntity) as cl:
        @implement(
            AddMethod(IRepo.add, entity='model'),
            GetMethod(IRepo.get, filters=['title']),
            UpdateMethod(IRepo.update, entity='model', filters=['title']),
            AddBatchMethod(IRepo.add_batch, dto_list='models'),
            GetAllMethod(IRepo.get_all_by_title, filters=['title']),
            GetListMethod(IRepo.get_model_list, offset='offset', limit='limit', filters=['title']),
            DeleteMethod(IRepo.delete, filters=['title']),
            config=RepositoryConfig(entity_type=NestedListEntity, collection=cl),
        )
        class MongoRepo:
            ...

        r: IRepo = MongoRepo()  # type: ignore
        await r.add(NestedListEntity('...', dtos=[SimpleEntity(x='1', y=1), SimpleEntity(x='1', y=1)]))
        assert True

        entity = await r.get(title='...')
        assert entity is not None
        assert entity.title
        assert len(entity.dtos) == 2

        entity.title = 'Updated title'
        updated_dto = await r.update(model=entity, title='...')
        assert updated_dto.title == 'Updated title'

        await r.add_batch(
            [
                NestedListEntity(title='1', dtos=[SimpleEntity(x='1', y=1)]),
                NestedListEntity(title='2', dtos=[SimpleEntity(x='2', y=2)]),
            ],
        )

        async for entity in r.get_all_by_title(title='1'):  # type: ignore
            assert entity.title == '1'

        dto_list = await r.get_model_list(title='2', limit=5, offset=0)
        assert len(dto_list) == 1
        assert dto_list[0].title == '2'

        deleted = await r.delete(title='1')
        assert deleted is True

        none = await r.get(title='1')
        assert none is None


async def test_implement_list_methods_with_specific_method_protocol():

    class IRepo:
        async def add(self, entity: NestedListEntity) -> None:
            ...

        # Change order of offset and remove its default value
        async def get_simple_dto_list_by_title(
            self, offset: int, title: str, limit: int = 20,
        ) -> list[SimpleEntity]:
            ...

        async def pop_dto_by_title(self, title: str) -> SimpleEntity:
            ...

        # Set entity as a second parameter
        async def append_dto_by_title(self, title: str, entity: SimpleEntity) -> None:
            ...

        async def remove_dto_by_title(self, entity: SimpleEntity, title: str) -> None:
            ...

    async with in_async_collection(NestedListEntity) as cl:

        @implement(
            AddMethod(IRepo.add, entity='entity'),
            ListGetFieldValuesMethod(
                source=IRepo.get_simple_dto_list_by_title, field_name='dtos',
                offset='offset',
                filters=['title'],
                limit='limit',
            ),
            ListPopMethod(IRepo.pop_dto_by_title, 'dtos', filters=['title']),
            ListAppendMethod(IRepo.append_dto_by_title, 'dtos', value='entity', filters=['title']),
            ListRemoveMethod(IRepo.remove_dto_by_title, 'dtos', value='entity', filters=['title']),
            config=RepositoryConfig(entity_type=NestedListEntity, collection=cl),
        )
        class MongoRepo:
            ...

        r: IRepo = MongoRepo()  # type: ignore
        title = '...'
        await r.add(NestedListEntity(title, dtos=[SimpleEntity(x='1', y=1), SimpleEntity(x='1', y=1)]))

        # All arguments are keywords arguments
        _ = await r.get_simple_dto_list_by_title(offset=0, title=title, limit=20)
        # All arguments are keywords arguments + parameter by default
        _ = await r.get_simple_dto_list_by_title(offset=0, title=title)
        # All arguments are keyword arguments + random order
        _ = await r.get_simple_dto_list_by_title(limit=5, title=title, offset=1)

        await r.append_dto_by_title(title=title, entity=SimpleEntity(x='3', y=3))
        await r.append_dto_by_title(title, SimpleEntity(x='2', y=2))
        await r.append_dto_by_title(entity=SimpleEntity(x='2', y=2), title=title)

        _ = await r.pop_dto_by_title(title)
        _ = await r.pop_dto_by_title(title=title)

        await r.remove_dto_by_title(title=title, entity=SimpleEntity(x='1', y=1))
        await r.remove_dto_by_title(SimpleEntity(x='1', y=3), title)
        await r.remove_dto_by_title(SimpleEntity(x='1', y=1), title=title)

        assert True


async def test_implement_integer_methods_with_specific_method_protocol() -> None:
    class IRepo:
        async def get(self, id: str) -> MixedEntity | None:
            ...

        async def add(self, entity: MixedEntity) -> None:
            ...

        async def update_year_with_weight(self, id: str, weight: int) -> None:
            ...

        async def update_year(self, id: str) -> None:
            ...

    async with in_async_collection(MixedEntity) as cl:
        @implement(
            AddMethod(IRepo.add, entity='entity'),
            GetMethod(IRepo.get, filters=['id']),
            IncrementIntegerFieldMethod(
                IRepo.update_year_with_weight, field_name='year', filters=['id'], weight='weight',
            ),
            IncrementIntegerFieldMethod(
                IRepo.update_year, field_name='year', filters=['id'], default_weight_value=-1,
            ),
            config=RepositoryConfig(entity_type=MixedEntity, collection=cl),
        )
        class MongoRepo:
            ...

    repo: IRepo = MongoRepo()  # type: ignore
    entity = MixedEntity(
        id='1',
        name='box',
        year=2025,
        main_box=Box('box_1', 'toy'),
        records=[1, 2, 3],
        boxs=[Box('box_list_1', 'car'), Box('box_list_2', 'table')],
    )
    await repo.add(entity=entity)

    await repo.update_year_with_weight(id='1', weight=5)

    updated_dto = await repo.get(id='1')
    assert updated_dto is not None
    assert updated_dto.year == 2030

    await repo.update_year(id='1')

    updated_dto = await repo.get(id='1')
    assert updated_dto is not None
    assert updated_dto.year == 2029
