from typing import Generic, Protocol, TypedDict

from mongorepo._methods.interfaces import MongorepoMethod
from mongorepo.collection_provider import CollectionProvider
from mongorepo.types import CollectionType, RepositoryConfig, SessionType


class MongorepoDict(Generic[SessionType, CollectionType], TypedDict, total=True):
    methods: dict[str, MongorepoMethod[SessionType]]
    repository_config: RepositoryConfig[CollectionType]
    collection_provider: CollectionProvider[CollectionType]


class HasMongorepoDict(Generic[SessionType, CollectionType], Protocol):
    __mongorepo__: MongorepoDict[SessionType, CollectionType]
