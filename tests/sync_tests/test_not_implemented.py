import pytest

from mongorepo.decorators import implements
from tests.common import NestedListDTO, SimpleDTO, custom_collection


# IDEA: to make substitute work with aray and integer fields methods


@pytest.mark.skip(reason='Not implemented yet')
def test_can_substitute_array_fields_methods():

    c = custom_collection(NestedListDTO)

    class IRepo:
        def add(self, dto: NestedListDTO) -> None:
            ...

        def get_simple_dto_list_by_title(
            self, title: str, offset: int = 0, limit: int = 20,
        ) -> list[SimpleDTO]:
            ...

        def pop_dto_by_title(self, title: str) -> SimpleDTO:
            ...

        def append_dto_by_title(self, title: str, dto: SimpleDTO) -> None:
            ...

        def remove_dto_by_title(self, title: str, dto: SimpleDTO) -> None:
            ...

    @implements(
        IRepo,
        add=IRepo.add,
        dtos__list=IRepo.get_simple_dto_list_by_title,
        dtos__pop=IRepo.pop_dto_by_title,
        dtos__append=IRepo.append_dto_by_title,
        dtos__remove=IRepo.remove_dto_by_title,
    )
    class MongoRepo:
        class Meta:
            collection = c
            dto = NestedListDTO

    r: IRepo = MongoRepo()  # type: ignore[reportAssignmentType]
    _ = NestedListDTO(dtos=[SimpleDTO(x='1', y=1)])
    r.add(_)

    dto_list = r.get_simple_dto_list_by_title(title=_.title)

    assert isinstance(dto_list, list)
    assert len(dto_list) == 1
    assert dto_list[0].x == '1'

    r.append_dto_by_title(title=_.title, dto=SimpleDTO(x='2', y=2))

    _dto = r.pop_dto_by_title(title=_.title)
    assert _dto
    assert _dto.x == '2'

    r.remove_dto_by_title(title=_.title, dto=SimpleDTO(x='1', y=1))

    dto_list = r.get_simple_dto_list_by_title(title=_.title)

    assert dto_list is not None
    assert len(dto_list) == 0

    c.drop()


@pytest.mark.skip(reason='Not implemented yet')
def test_can_substitute_integer_fields_methods():
    c = custom_collection(SimpleDTO)

    class IRepo:
        def get(self, x: str) -> SimpleDTO | None:
            ...

        def add(self, dto: SimpleDTO) -> None:
            ...

        def incr(self, x: str) -> None:
            ...

        def decr(self, x: str) -> None:
            ...

    @implements(
        IRepo,
        get=IRepo.get,
        add=IRepo.add,
        incr__y=IRepo.incr,
        decr__y=IRepo.decr,
    )
    class MongoRepo:
        class Meta:
            collection = c
            dto = NestedListDTO

    r: IRepo = MongoRepo()  # type: ignore[reportAssignmentType]
    _ = SimpleDTO(x='1', y=1)
    r.add(_)

    r.incr(x='1')
    r.incr(x='1')
    r.incr(x='1')  # y = 4

    incremented = r.get(x='1')

    assert incremented is not None
    assert incremented.y == 4

    r.decr(x='1')  # y = 3

    _dto = r.get(x='1')
    assert _dto
    assert _dto.y == 3

    c.drop()
