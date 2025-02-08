import pytest

from mongorepo import implements
from mongorepo.exceptions import InvalidMethodNameException
from tests.common import NestedListDTO, SimpleDTO, custom_collection


async def test_can_substitute_array_fields_methods():

    c = custom_collection(NestedListDTO, async_client=True)

    class IRepo:
        async def add(self, dto: NestedListDTO) -> None:
            ...

        async def get_simple_dto_list_by_title(
            self, title: str, offset: int = 0, limit: int = 20,
        ) -> list[SimpleDTO]:
            ...

        async def pop_dto_by_title(self, title: str) -> SimpleDTO:
            ...

        async def append_dto_by_title(self, dto: SimpleDTO, title: str) -> None:
            ...

        async def remove_dto_by_title(self, dto: SimpleDTO, title: str) -> None:
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
    await r.add(_)

    dto_list = await r.get_simple_dto_list_by_title(title=_.title)

    assert isinstance(dto_list, list)
    assert len(dto_list) == 1
    assert dto_list[0].x == '1'

    await r.append_dto_by_title(title=_.title, dto=SimpleDTO(x='2', y=2))

    _dto = await r.pop_dto_by_title(title=_.title)
    assert _dto
    assert _dto.x == '2'

    await r.remove_dto_by_title(title=_.title, dto=SimpleDTO(x='1', y=1))

    dto_list = await r.get_simple_dto_list_by_title(title=_.title, offset=0, limit=20)

    assert dto_list is not None
    assert len(dto_list) == 0

    c.drop()


async def test_cannot_implement_array_methods():
    c = custom_collection(NestedListDTO, async_client=True)

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


async def test_can_substitute_integer_fields_methods():
    c = custom_collection(SimpleDTO, async_client=True)

    class IRepo:
        async def get(self, x: str) -> SimpleDTO | None:
            ...

        async def add(self, dto: SimpleDTO) -> None:
            ...

        async def incr(self, x: str) -> None:
            ...

        async def decr(self, x: str) -> None:
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
    await r.add(_)

    await r.incr(x='1')
    await r.incr(x='1')
    await r.incr(x='1')  # y = 4

    incremented = await r.get(x='1')

    assert incremented is not None
    assert incremented.y == 4

    await r.decr(x='1')  # y = 3

    _dto = await r.get(x='1')
    assert _dto
    assert _dto.y == 3

    c.drop()
