from dataclasses import Field, dataclass
from enum import Enum
from typing import Any, ClassVar, Protocol, TypeVar


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DTO = TypeVar('DTO', bound=DataclassInstance)
_DTOField = TypeVar('_DTOField', bound=DataclassInstance)


@dataclass(repr=False, slots=True, eq=False)
class Index:
    """Allows to specify extra information about mongodb index"""
    field: str
    name: str | None = None
    desc: bool = True
    unique: bool = False


class Access(int, Enum):
    """
    Use to indicate method access in a repository, see also `mongorepo.utils.get_prefix` function
    """
    PUBLIC = 0
    PROTECTED = 1
    PRIVATE = 2
