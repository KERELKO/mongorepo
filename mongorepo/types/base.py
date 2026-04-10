from dataclasses import Field as DataclassField
from typing import Any, Callable, ClassVar, Protocol, TypeVar

from motor.motor_asyncio import (
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
)
from pymongo.client_session import ClientSession
from pymongo.collection import Collection


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, DataclassField[Any]]]


Entity = TypeVar("Entity")
CollectionType = TypeVar('CollectionType', AsyncIOMotorCollection, Collection[Any])
SessionType = TypeVar('SessionType', AsyncIOMotorClientSession, ClientSession)
ToEntityConverter = Callable[[dict[str, Any], type[Entity]], Entity]
ToDocumentConverter = Callable[[Entity], dict[str, Any]]
