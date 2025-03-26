# type: ignore
import asyncio
import random

from mongorepo import BaseAsyncMongoRepository, Index
from tests.common import SimpleDTO, collection_for_simple_dto


async def test_all_methods_with_inherited_repo():
    cl = collection_for_simple_dto(async_client=True)

    class TestMongoRepository(BaseAsyncMongoRepository[SimpleDTO]):
        class Meta:
            index = Index(field='y', name='async_index_y', unique=True)
            collection = cl

    num = random.randint(1, 12346)
    unum = random.randint(1, 4567)
    repo = TestMongoRepository()

    new_dto: SimpleDTO = await repo.add(SimpleDTO(x='hey', y=num))
    assert new_dto.x == 'hey'

    updated_dto = await repo.update(SimpleDTO(x='hey all!', y=unum), y=num)
    assert updated_dto.x == 'hey all!'

    async for selected_dto in repo.get_all():
        assert selected_dto.x == 'hey all!'
        break

    dto: SimpleDTO | None = await repo.get(y=unum)
    assert dto is not None

    is_deleted = await repo.delete(y=unum)
    assert is_deleted is True

    dto = await repo.get(y=unum)
    assert dto is None

    await asyncio.sleep(2)

    cl.drop()
