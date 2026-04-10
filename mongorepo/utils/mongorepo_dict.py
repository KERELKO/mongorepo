from mongorepo.exceptions import MongorepoException
from mongorepo.types import CollectionType, RepositoryConfig, SessionType
from mongorepo.types.collection_provider import CollectionProvider
from mongorepo.types.mongorepo_dict import MongorepoDict


def get_or_create_mongorepo_dict(
    cls: type,
    collection_provider: CollectionProvider[CollectionType] | None = None,
    repository_config: RepositoryConfig[CollectionType] | None = None,
) -> MongorepoDict[SessionType, CollectionType]:
    if hasattr(cls, '__mongorepo__'):
        __mongorepo__: MongorepoDict = getattr(
            cls, '__mongorepo__',
        )
    else:
        if not collection_provider or not repository_config:
            raise MongorepoException(
                message="Cannot create MongorepoDict instance without "
                "collection_provider or repository_config",
            )
        __mongorepo__ = MongorepoDict(
            collection_provider=collection_provider,
            methods={},
            repository_config=repository_config,
        )
    return __mongorepo__
