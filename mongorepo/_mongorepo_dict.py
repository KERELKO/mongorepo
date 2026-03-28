from typing import Generic, Protocol, TypedDict

from mongorepo._methods.interfaces import MongorepoMethod
from mongorepo.collection_provider import CollectionProvider
from mongorepo.types import CollectionType, RepositoryConfig, SessionType


class MongorepoDict(Generic[SessionType, CollectionType], TypedDict, total=True):
    methods: dict[str, MongorepoMethod[SessionType]]
    repository_config: RepositoryConfig[CollectionType]
    collection_provider: CollectionProvider[CollectionType]


def mongorepo_dict_factory(
    repository_config: RepositoryConfig[CollectionType],
    collection_provider: CollectionProvider[CollectionType],
    methods: dict[str, MongorepoMethod[SessionType]] | None = None,
) -> MongorepoDict[SessionType, CollectionType]:
    methods = methods or {}
    return MongorepoDict(
        repository_config=repository_config,
        collection_provider=collection_provider,
        methods=methods,
    )


class HasMongorepoDict(Generic[SessionType, CollectionType], Protocol):
    __mongorepo__: MongorepoDict[SessionType, CollectionType]
