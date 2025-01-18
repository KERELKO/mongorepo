from typing import Iterable

from mongorepo import implements
from mongorepo.implements.methods import (
    AddBatchMethod,
    AddMethod,
    DecrementIntergerFieldMethod,
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
from tests.common import Box, MixDTO, NestedListDTO, SimpleDTO, in_collection


def test_implements_crud_with_specific_method_protocol():
    """Test `@implements` decorator with classes that implement
    `SpecificMethod` protocol."""

    with in_collection(NestedListDTO) as c:
        class IRepo:
            def get(self, title: str) -> NestedListDTO:
                ...

            def add(self, model: NestedListDTO) -> NestedListDTO:
                ...

            def update(self, model: NestedListDTO, title: str) -> NestedListDTO:
                ...

            def delete(self, title: str) -> bool:
                ...

            def add_batch(self, models: list[NestedListDTO]) -> None:
                ...

            def get_all_by_title(self, title: str) -> Iterable[NestedListDTO]:
                ...

            def get_model_list(
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
        r.add(NestedListDTO('...', dtos=[SimpleDTO(x='1', y=1), SimpleDTO(x='1', y=1)]))
        assert True

        dto = r.get(title='...')
        assert dto is not None
        assert dto.title
        assert len(dto.dtos) == 2

        dto.title = 'Updated title'
        updated_dto = r.update(model=dto, title='...')
        assert updated_dto.title == 'Updated title'

        r.add_batch(
            [
                NestedListDTO(title='1', dtos=[SimpleDTO(x='1', y=1)]),
                NestedListDTO(title='2', dtos=[SimpleDTO(x='2', y=2)]),
            ],
        )

        dtos = r.get_all_by_title(title='1')
        for dto in dtos:
            assert dto.title == '1'

        dto_list = r.get_model_list(title='2', limit=5, offset=0)
        assert len(dto_list) == 1
        assert dto_list[0].title == '2'

        deleted = r.delete(title='1')
        assert deleted is True

        none = r.get(title='1')
        assert none is None


def test_implements_list_methods_with_specific_method_protocol():

    class IRepo:
        def add(self, dto: NestedListDTO) -> None:
            ...

        # Change order of offset and remove its default value
        def get_simple_dto_list_by_title(
            self, offset: int, title: str, limit: int = 20,
        ) -> list[SimpleDTO]:
            ...

        def pop_dto_by_title(self, title: str) -> SimpleDTO:
            ...

        # Set dto as a second parameter
        def append_dto_by_title(self, title: str, dto: SimpleDTO) -> None:
            ...

        def remove_dto_by_title(self, dto: SimpleDTO, title: str) -> None:
            ...

    with in_collection(NestedListDTO) as c:

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
        r.add(NestedListDTO(title, dtos=[SimpleDTO(x='1', y=1), SimpleDTO(x='1', y=1)]))

        # All arguments are keywords arguments
        _ = r.get_simple_dto_list_by_title(offset=0, title=title, limit=20)
        # All arguments are keywords arguments + parameter by default
        _ = r.get_simple_dto_list_by_title(offset=0, title=title)
        # All arguments are keyword arguments + random order
        _ = r.get_simple_dto_list_by_title(limit=5, title=title, offset=1)

        r.append_dto_by_title(title=title, dto=SimpleDTO(x='3', y=3))
        r.append_dto_by_title(title, SimpleDTO(x='2', y=2))
        r.append_dto_by_title(dto=SimpleDTO(x='2', y=2), title=title)

        _ = r.pop_dto_by_title(title)
        _ = r.pop_dto_by_title(title=title)

        r.remove_dto_by_title(title=title, dto=SimpleDTO(x='1', y=1))
        r.remove_dto_by_title(SimpleDTO(x='1', y=3), title)
        r.remove_dto_by_title(SimpleDTO(x='1', y=1), title=title)

        assert True


def test_implements_integer_methods_with_specific_method_protocol() -> None:
    class IRepo:
        def get(self, id: str) -> MixDTO | None:
            ...

        def add(self, dto: MixDTO) -> None:
            ...

        def update_year_with_weight(self, id: str, weight: int) -> None:
            ...

        def update_year(self, id: str) -> None:
            ...

    with in_collection(MixDTO) as coll:
        @implements(
            IRepo,
            AddMethod(IRepo.add, dto='dto'),
            GetMethod(IRepo.get, filters=['id']),
            IncrementIntegerFieldMethod(
                IRepo.update_year_with_weight, field_name='year', filters=['id'], weight='weight',
            ),
            DecrementIntergerFieldMethod(
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
    repo.add(dto=dto)

    repo.update_year_with_weight(id='1', weight=5)

    updated_dto = repo.get(id='1')
    assert updated_dto is not None
    assert updated_dto.year == 2030

    repo.update_year(id='1')

    updated_dto = repo.get(id='1')
    assert updated_dto is not None
    assert updated_dto.year == 2029
