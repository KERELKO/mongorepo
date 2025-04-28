from dataclasses import Field, dataclass
from enum import Enum
from typing import Any, ClassVar, Generic, Protocol, TypedDict, TypeVar, cast

from motor.motor_asyncio import (
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
)
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from . import exceptions


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DTO = TypeVar('DTO', bound=Dataclass)
CollectionType = TypeVar('CollectionType', AsyncIOMotorCollection, Collection[Any])
SessionType = TypeVar('SessionType', AsyncIOMotorClientSession, ClientSession)


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


class MetaAttributes(Generic[CollectionType], TypedDict, total=True):
    dto: type[Dataclass] | None
    collection: CollectionType | None
    index: str | Index | None
    method_access: Access | None
    id_field: str | None


class CollectionProvider(Generic[CollectionType]):
    def __init__(self, obj: Any, collection: CollectionType | None = None):
        self.collection: CollectionType | None = collection
        self.obj = obj

    def provide(self) -> CollectionType:
        # First check if collection already provided
        if self.collection is not None:
            return self.collection

        # Check if collection present in object attributes
        if (__mongorepo__ := getattr(self.obj, '__mongorepo__', None)) is not None:
            collection: CollectionType = __mongorepo__['collection_provider'].collection
            if collection is not None:
                self.collection = collection
                return collection

        # Check if collection in Meta class
        meta = self.obj.__dict__.get('Meta', None)
        if meta is not None:
            if (c := getattr(meta, 'collection', None)) is not None:
                if not isinstance(c, (AsyncIOMotorCollection, Collection)):
                    raise exceptions.NoCollectionException
                self.collection = cast(CollectionType, c)
                return self.collection
        # If no collection raise exception
        raise exceptions.NoCollectionException('Collection cannot be found', with_meta=False)
