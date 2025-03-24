from typing import Generic, Protocol, TypedDict

from ._base import CollectionProvider, CollectionType, SessionType
from ._methods.interfaces import MongorepoMethod


class MongorepoDict(Generic[SessionType, CollectionType], TypedDict, total=True):
    methods: dict[str, MongorepoMethod[SessionType]]
    collection_provider: CollectionProvider[CollectionType]


class HasMongorepoDict(Generic[SessionType, CollectionType], Protocol):
    __mongorepo__: MongorepoDict[SessionType, CollectionType]


def default_mongorepo_dict(
    collection_provider: CollectionProvider[CollectionType],
    methods: dict[str, MongorepoMethod[SessionType]] | None = None,
) -> MongorepoDict[SessionType, CollectionType]:
    methods = methods or {}
    return MongorepoDict(collection_provider=collection_provider, methods=methods)
