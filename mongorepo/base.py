from dataclasses import Field, dataclass
from enum import Enum
from typing import Any, ClassVar, Protocol, TypeVar


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DTO = TypeVar('DTO', bound=DataclassInstance)


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
