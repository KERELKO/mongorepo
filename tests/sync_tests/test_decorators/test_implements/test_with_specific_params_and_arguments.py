from mongorepo import implements
from mongorepo.implements.methods import (
    AddMethod,
    ListAppendMethod,
    ListGetFieldValuesMethod,
    ListPopMethod,
    ListRemoveMethod,
)
from tests.common import NestedListDTO, SimpleDTO, custom_collection


def test_can_change_order_of_repo_parameters_and_passed_arguments():

    c = custom_collection(NestedListDTO)

    class IRepo:
        def add(self, dto: NestedListDTO) -> None:
            ...

        # Change order of offset and remove its default value
        def get_simple_dto_list_by_title(  # type: ignore[empty-body]
            self, offset: int, title: str, limit: int = 20,
        ) -> list[SimpleDTO]:
            ...

        def pop_dto_by_title(self, title: str) -> SimpleDTO:  # type: ignore[empty-body]
            ...

        # Set dto as a second parameter
        def append_dto_by_title(self, title: str, dto: SimpleDTO) -> None:
            ...

        def remove_dto_by_title(self, dto: SimpleDTO, title: str) -> None:
            ...

    @implements(
        IRepo,
        AddMethod(IRepo.add, dto='dto'),
        ListGetFieldValuesMethod(
            IRepo.get_simple_dto_list_by_title,
            field_name='dtos',
            filters=['title'],
            offset='offset',
            limit='limit',
        ),
        ListPopMethod(IRepo.pop_dto_by_title, field_name='dtos', filters=['title']),
        ListAppendMethod(
            IRepo.append_dto_by_title, filters=['title'], field_name='dtos', value='dto',
        ),
        ListRemoveMethod(
            IRepo.remove_dto_by_title, value='dto', field_name='dtos', filters=['title'],
        ),
    )
    class MongoRepo:
        class Meta:
            collection = c
            dto = NestedListDTO

    r: IRepo = MongoRepo()  # type: ignore
    title = 'title'
    r.add(NestedListDTO(title, dtos=[SimpleDTO(x='1', y=1), SimpleDTO(x='1', y=1)]))

    _ = r.get_simple_dto_list_by_title(offset=0, title=title, limit=20)
    _ = r.get_simple_dto_list_by_title(offset=0, title=title)
    _ = r.get_simple_dto_list_by_title(limit=5, title='title', offset=1)
    _ = r.get_simple_dto_list_by_title(offset=5, title='title')

    r.append_dto_by_title(title=title, dto=SimpleDTO(x='3', y=3))
    r.append_dto_by_title(title, SimpleDTO(x='2', y=2))
    r.append_dto_by_title(dto=SimpleDTO(x='2', y=2), title=title)

    _ = r.pop_dto_by_title(title)
    _ = r.pop_dto_by_title(title=title)

    r.remove_dto_by_title(title=title, dto=SimpleDTO(x='1', y=1))
    r.remove_dto_by_title(SimpleDTO(x='1', y=3), title)
    r.remove_dto_by_title(SimpleDTO(x='1', y=1), title=title)

    c.drop()

    assert True
