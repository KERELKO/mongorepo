from dataclasses import Field as DataclassField
from dataclasses import dataclass
from enum import Enum
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


class MethodAccess(int, Enum):
    """Use to indicate method access in a repository."""
    PUBLIC = 0
    PROTECTED = 1
    PRIVATE = 2


def get_method_access_prefix(access: MethodAccess | None, cls: type | None = None) -> str:
    """
    Returns string prefix according to MethodAccess value,
    * it can be `'_'`, `'__'`, `_{cls.__name__}__` or `''`
    """
    match access:
        case MethodAccess.PRIVATE:
            prefix = f'_{cls.__name__}__' if cls else '__'
        case MethodAccess.PROTECTED:
            prefix = '_'
        case MethodAccess.PUBLIC | None:
            prefix = ''
    return prefix


@dataclass(slots=True)
class RepositoryConfig[CollectionType]:
    """Config for Mongorepo repository."""
    entity_type: type
    """Type of the entity on which repository will operate."""
    collection: CollectionType | None = None
    """Collection which mongorepo will use to access DB."""
    method_access: MethodAccess | None = None
    """Access to mongorepo methods."""

    to_document_converter: Callable[[Any], dict] | None = None
    to_entity_converter: Callable[[dict, type], Any] | None = None
