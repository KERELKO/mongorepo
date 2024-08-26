from typing import Callable

from motor.motor_asyncio import AsyncIOMotorCollection

from mongorepo.utils import raise_exc
from mongorepo import DTO, exceptions


def _update_integer_field_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    field_name: str,
    _weight: int = 1,
) -> Callable:
    async def update_integer_field(self, weight: int | None = None, **filters) -> None:
        w = weight if weight is not None else _weight
        document = await collection.find_one_and_update(
            filter=filters, update={'$inc': {field_name: w}}, return_document=True,
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
    return update_integer_field
