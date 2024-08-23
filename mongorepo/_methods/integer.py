from typing import Callable

from pymongo.collection import Collection
from mongorepo.utils import raise_exc
from mongorepo import DTO, exceptions


def _update_integer_field_method(
    dto_type: type[DTO], collection: Collection, field_name: str, _weight: int = 1,
) -> Callable:
    def update_integer_field(self, weight: int | None = None, **filters) -> None:
        w = weight if weight is not None else _weight
        doc = collection.update_one(
            filter=filters, update={'$inc': {field_name: w}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not doc else ...
    return update_integer_field
