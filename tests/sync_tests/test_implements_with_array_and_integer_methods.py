import pytest

from mongorepo.decorators import implements
from mongorepo.exceptions import InvalidMethodNameException
from tests.common import NestedListDTO, SimpleDTO, custom_collection


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

        def append_dto_by_title(self, dto: SimpleDTO, title: str) -> None:
            ...

        def remove_dto_by_title(self, dto: SimpleDTO, title: str) -> None:
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

    dto_list = r.get_simple_dto_list_by_title(title=_.title, offset=0, limit=20)

    assert dto_list is not None
    assert len(dto_list) == 0

    c.drop()


def test_cannot_implement_array_methods():
    c = custom_collection(NestedListDTO)

    class IRepo:
        def get_simple_dto_list_by_title(
            self, title: str, offset: int = 0, limit: int = 20,
        ) -> list[SimpleDTO]:
            ...

    with pytest.raises(InvalidMethodNameException):
        @implements(
            IRepo,
            # Invalid mongorepo method name
            dtos__my_list=IRepo.get_simple_dto_list_by_title,
        )
        class MongoRepo:
            class Meta:
                collection = c
                dto = NestedListDTO

    c.drop()


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
            dto = SimpleDTO

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


@pytest.mark.skip('Impossible to pass on v2.0.0')
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

    r: IRepo = MongoRepo()  # type: ignore
    title = 'title'
    r.add(NestedListDTO(title, dtos=[SimpleDTO(x='1', y=1), SimpleDTO(x='1', y=1)]))

    _ = r.get_simple_dto_list_by_title(offset=0, title=title, limit=20)
    _ = r.get_simple_dto_list_by_title(offset=0, title=title)
    _ = r.get_simple_dto_list_by_title(limit=5, title='title', offset=1)
    _ = r.get_simple_dto_list_by_title(offset=5, title='title')

    # Alaways falls here because in `update_list`
    # closure of `_update_list_field_method` of arrays methods
    # `title` goes to `value`, and `dto` goes to `**filters` because of that
    # it's impossible to replace params without any customization from the user, now the only
    # solution is to replace positition of `title` and `dto` in IRepo (base_cls)
    # what is incorrect from the look of architecture flow
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
