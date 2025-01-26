import asyncio
from uuid import uuid4

import mongorepo
from tests.common import ComplicatedDTO, in_async_collection


async def test_can_create_index_in_background() -> None:
    index_name = f'complicated-dto-index-{uuid4()}'

    async with in_async_collection(ComplicatedDTO) as c:
        @mongorepo.async_repository
        class MyRepository:
            class Meta:
                collection = c
                dto = ComplicatedDTO
                index = mongorepo.Index(field='year', name=index_name)

        await asyncio.sleep(1)
        assert index_name in await c.index_information()
