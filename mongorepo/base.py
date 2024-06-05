from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Protocol, TypeVar


DTO = TypeVar('DTO')


@dataclass(repr=False, slots=True, eq=False)
class Index:
    field: str
    name: str | None = None
    desc: bool = True
    unique: bool = False


class Access(int, Enum):
    PUBLIC = 0
    PROTECTED = 1
    PRIVATE = 2


class IMongoRepository(Protocol[DTO]):
    def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        raise NotImplementedError

    def get_all(self, **filters: Any) -> Iterable[DTO]:
        raise NotImplementedError

    def update(self, dto: DTO, **filter_: Any) -> DTO:
        raise NotImplementedError

    def delete(self, _id: str | None = None, **filters: Any) -> bool:
        raise NotImplementedError

    def create(self, dto: DTO) -> DTO:
        raise NotImplementedError
