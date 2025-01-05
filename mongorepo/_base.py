from dataclasses import Field, dataclass
from enum import Enum
from typing import Any, ClassVar, Protocol, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DTO = TypeVar('DTO', bound=DataclassInstance)
_DTOField = TypeVar('_DTOField', bound=DataclassInstance)


@dataclass(repr=False, slots=True, eq=False)
class Index:
    """Allows to specify extra information about mongodb index."""
    field: str
    name: str | None = None
    desc: bool = True
    unique: bool = False


class Access(int, Enum):
    """Use to indicate method access in a repository."""
    PUBLIC = 0
    PROTECTED = 1
    PRIVATE = 2


@dataclass(eq=False)
class MethodDeps:
    """DTO for mongorepo methods dependencies.

    ### includes:
    ```
    collection: Collection | AsyncIOMotorCollection | None = None
    dto: type[DTO] | None = None
    id_field: str | None = None
    field_name: str | None = None
    ```

    """
    collection: Collection | AsyncIOMotorCollection
    dto_type: type
    id_field: str | None = None
    custom_field_method_name: str | None = None
    update_integer_weight: int | None = None
