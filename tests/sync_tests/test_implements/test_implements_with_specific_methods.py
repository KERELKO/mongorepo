import pytest

from mongorepo import Method, implements
from mongorepo._implements.methods import AddMethod, GetMethod
from tests.common import NestedListDTO, SimpleDTO, custom_collection


def tests_implements_decorator_with_method_class():
    """Test `@implements` decorator with classes that implement
    `SpecificMethod` protocol."""

    c = custom_collection(NestedListDTO)

    class IRepo:
        def get(self, title: str) -> NestedListDTO:
            ...

        def add(self, dto: NestedListDTO) -> None:
            ...

    @implements(
        IRepo,
        GetMethod(IRepo.get, filters=['title']),
        AddMethod(IRepo.add, dto='dto'),
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


@pytest.mark.skip()
def test_can_change_order_of_repo_parameters_and_passed_arguments():

    c = custom_collection(NestedListDTO)

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

    @implements(
        IRepo,
        add=Method(
            IRepo.add, dto='dto',
        ),
        dtos__list=Method(
            IRepo.get_simple_dto_list_by_title, offset='offset', limit='limit', title='filters',
        ),
        dtos__pop=Method(
            IRepo.pop_dto_by_title, title='filters',
        ),
        dtos__append=Method(
            IRepo.append_dto_by_title, dto='value', title='filters',
        ),
        dtos__remove=Method(
            IRepo.remove_dto_by_title, title='filters', dto='value',
        ),
    )
    class MongoRepo:
        class Meta:
            collection = c
            dto = NestedListDTO

    r: IRepo = MongoRepo()  # type: ignore
    title = '...'
    r.add(NestedListDTO(title, dtos=[SimpleDTO(x='1', y=1), SimpleDTO(x='1', y=1)]))

    _ = r.get_simple_dto_list_by_title(offset=0, title=title, limit=20)
    _ = r.get_simple_dto_list_by_title(offset=0, title=title)
    _ = r.get_simple_dto_list_by_title(limit=5, title=title, offset=1)
    _ = r.get_simple_dto_list_by_title(offset=5, title=title)

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
