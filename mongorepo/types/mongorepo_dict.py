from typing import Generic, Protocol, TypedDict

from mongorepo._methods.interfaces import MongorepoMethod

from .base import CollectionType, SessionType
from .collection_provider import CollectionProvider
from .repository_config import RepositoryConfig


class MongorepoDict(Generic[SessionType, CollectionType], TypedDict, total=True):
    methods: dict[str, MongorepoMethod[SessionType]]
    repository_config: RepositoryConfig[CollectionType]
    collection_provider: CollectionProvider[CollectionType]


class HasMongorepoDict(Generic[SessionType, CollectionType], Protocol):
    __mongorepo__: MongorepoDict[SessionType, CollectionType]
