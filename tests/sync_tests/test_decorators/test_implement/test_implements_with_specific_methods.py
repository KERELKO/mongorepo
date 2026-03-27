from typing import Iterable

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
from tests.common import Box, MixedEntity, NestedListEntity, SimpleEntity, in_collection


def test_implement_crud_with_specific_method_protocol():
    """Test `@implement` decorator with classes that implement `SpecificMethod`
    protocol."""

    with in_collection(NestedListEntity) as c:
        class IRepo:
            def get(self, title: str) -> NestedListEntity:  # type: ignore[empty-body]
                ...

            def add(self, model: NestedListEntity) -> NestedListEntity:  # type: ignore[empty-body]
                ...

            def update(  # type: ignore[empty-body]
                self, model: NestedListEntity, title: str,
            ) -> NestedListEntity:
                ...

            def delete(self, title: str) -> bool:  # type: ignore[empty-body]
                ...

            def add_batch(self, models: list[NestedListEntity]) -> None:  # type: ignore[empty-body]
                ...

            def get_all_by_title(  # type: ignore[empty-body]
                self, title: str,
            ) -> Iterable[NestedListEntity]:
                ...

            def get_model_list(  # type: ignore[empty-body]
                self, title: str, limit: int, offset: int = 20,
            ) -> list[NestedListEntity]:
                ...

        @implement(
            AddMethod(IRepo.add, entity='model'),
            GetMethod(IRepo.get, filters=['title']),
            UpdateMethod(IRepo.update, entity='model', filters=['title']),
            AddBatchMethod(IRepo.add_batch, dto_list='models'),
            GetAllMethod(IRepo.get_all_by_title, filters=['title']),
            GetListMethod(IRepo.get_model_list, offset='offset', limit='limit', filters=['title']),
            DeleteMethod(IRepo.delete, filters=['title']),
        )
        class MongoRepo:
            class Meta:
                collection = c
                entity = NestedListEntity

        r: IRepo = MongoRepo()  # type: ignore
        r.add(NestedListEntity('...', dtos=[SimpleEntity(x='1', y=1), SimpleEntity(x='1', y=1)]))
        assert True

        entity = r.get(title='...')
        assert entity is not None
        assert entity.title
        assert len(entity.dtos) == 2

        entity.title = 'Updated title'
        updated_dto = r.update(model=entity, title='...')
        assert updated_dto.title == 'Updated title'

        r.add_batch(
            [
                NestedListEntity(title='1', dtos=[SimpleEntity(x='1', y=1)]),
                NestedListEntity(title='2', dtos=[SimpleEntity(x='2', y=2)]),
            ],
        )

        dtos = r.get_all_by_title(title='1')
        for entity in dtos:
            assert entity.title == '1'

        dto_list = r.get_model_list(title='2', limit=5, offset=0)
        assert len(dto_list) == 1
        assert dto_list[0].title == '2'

        deleted = r.delete(title='1')
        assert deleted is True

        none = r.get(title='1')
        assert none is None


def test_implement_list_methods_with_specific_method_protocol():

    class IRepo:
        def add(self, entity: NestedListEntity) -> None:
            ...

        # Change order of offset and remove its default value
        def get_simple_dto_list_by_title(  # type: ignore[empty-body]
            self, offset: int, title: str, limit: int = 20,
        ) -> list[SimpleEntity]:
            ...

        def pop_dto_by_title(self, title: str) -> SimpleEntity:  # type: ignore[empty-body]
            ...

        # Set entity as a second parameter
        def append_dto_by_title(self, title: str, entity: SimpleEntity) -> None:
            ...

        def remove_dto_by_title(self, entity: SimpleEntity, title: str) -> None:
            ...

    with in_collection(NestedListEntity) as c:

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
        )
        class MongoRepo:
            class Meta:
                collection = c
                entity = NestedListEntity

        r: IRepo = MongoRepo()  # type: ignore
        title = '...'
        r.add(NestedListEntity(title, dtos=[SimpleEntity(x='1', y=1), SimpleEntity(x='1', y=1)]))

        # All arguments are keywords arguments
        _ = r.get_simple_dto_list_by_title(offset=0, title=title, limit=20)
        # All arguments are keywords arguments + parameter by default
        _ = r.get_simple_dto_list_by_title(offset=0, title=title)
        # All arguments are keyword arguments + random order
        _ = r.get_simple_dto_list_by_title(limit=5, title=title, offset=1)

        r.append_dto_by_title(title=title, entity=SimpleEntity(x='3', y=3))
        r.append_dto_by_title(title, SimpleEntity(x='2', y=2))
        r.append_dto_by_title(entity=SimpleEntity(x='2', y=2), title=title)

        _ = r.pop_dto_by_title(title)
        _ = r.pop_dto_by_title(title=title)

        r.remove_dto_by_title(title=title, entity=SimpleEntity(x='1', y=1))
        r.remove_dto_by_title(SimpleEntity(x='1', y=3), title)
        r.remove_dto_by_title(SimpleEntity(x='1', y=1), title=title)

        assert True


def test_implement_integer_methods_with_specific_method_protocol() -> None:
    class IRepo:
        def get(self, id: str) -> MixedEntity | None:
            ...

        def add(self, entity: MixedEntity) -> None:
            ...

        def update_year_with_weight(self, id: str, weight: int) -> None:
            ...

        def update_year(self, id: str) -> None:
            ...

    with in_collection(MixedEntity) as coll:
        @implement(
            AddMethod(IRepo.add, entity='entity'),
            GetMethod(IRepo.get, filters=['id']),
            IncrementIntegerFieldMethod(
                IRepo.update_year_with_weight, field_name='year', filters=['id'], weight='weight',
            ),
            IncrementIntegerFieldMethod(
                IRepo.update_year, field_name='year', filters=['id'], default_weight_value=-1,
            ),
        )
        class MongoRepo:
            class Meta:
                entity = MixedEntity
                collection = coll

    repo: IRepo = MongoRepo()  # type: ignore
    entity = MixedEntity(
        id='1',
        name='box',
        year=2025,
        main_box=Box('box_1', 'toy'),
        records=[1, 2, 3],
        boxs=[Box('box_list_1', 'car'), Box('box_list_2', 'table')],
    )
    repo.add(entity=entity)

    repo.update_year_with_weight(id='1', weight=5)

    updated_dto = repo.get(id='1')
    assert updated_dto is not None
    assert updated_dto.year == 2030

    repo.update_year(id='1')

    updated_dto = repo.get(id='1')
    assert updated_dto is not None
    assert updated_dto.year == 2029
