from mongorepo.implement import AddMethod, implement
from tests.common import SimpleDTO, in_async_collection


async def test_can_use_slots():
    class IRepo:
        async def add(self, simple: SimpleDTO):
            ...

    async with in_async_collection(SimpleDTO) as coll:
        @implement(AddMethod(IRepo.add, dto='simple'))
        class Repo:
            class Meta:
                dto = SimpleDTO
                collection = coll

            __slots__ = 'x',

            def __init__(self, x: int = 1):
                self.x = x

        repo: IRepo = Repo()  # type: ignore
        simple = await repo.add(SimpleDTO(x='1', y=1))
        print(simple)
