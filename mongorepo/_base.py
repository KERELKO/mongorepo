from dataclasses import Field, dataclass
from enum import Enum, StrEnum
from typing import (
    Any,
    ClassVar,
    Generic,
    Literal,
    Protocol,
    TypedDict,
    TypeVar,
)

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DTO = TypeVar('DTO', bound=Dataclass)
_DTOField = TypeVar('_DTOField', bound=Dataclass)
CollectionType = TypeVar('CollectionType', AsyncIOMotorCollection, Collection[Any])


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


class MetaAttributes(Generic[CollectionType], TypedDict, total=True):
    dto: type[Dataclass] | None
    collection: CollectionType | None
    index: str | Index | None
    method_access: Access | None
    substitute: dict[str, Any] | None
    id_field: str | None


class MethodAction(StrEnum):
    GET = 'get'
    GET_LIST = 'get_list'
    GET_ALL = 'get_all'
    UPDATE = 'update'
    ADD = 'add'
    ADD_BATCH = 'add_batch'
    DELETE = 'delete'

    INTEGER_INCREMENT = 'incr__'
    INTEGER_DECREMENT = 'decr__'

    LIST_APPEND = '__append'
    LIST_REMOVE = '__remove'
    LIST_POP = '__pop'
    LIST_FIELD_VALUES = '__list'

    def as_mongo_action(self) -> str:
        match self:
            case self.LIST_APPEND:
                return '$push'
            case self.LIST_REMOVE:
                return '$pull'
            case self.LIST_POP:
                return '$pop'
        return self.value


class ParameterEnum(StrEnum):
    FILTER = 'filters'
    OFFSET = 'offset'
    LIMIT = 'limit'
    DTO = 'dto'
    VALUE = 'value'
    WEIGHT = 'weight'
    FILTER_ALIAS = '__filter_alias'


LParameter = Literal[
    ParameterEnum.FILTER,
    ParameterEnum.OFFSET,
    ParameterEnum.LIMIT,
    ParameterEnum.DTO,
    ParameterEnum.VALUE,
    ParameterEnum.WEIGHT,
    ParameterEnum.FILTER_ALIAS,
]

MONGOREPO_COLLECTION = '_mongorepo_collection'
