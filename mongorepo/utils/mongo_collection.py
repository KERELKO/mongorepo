from typing import Any, overload

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo._mongorepo_dict import HasMongorepoDict
from mongorepo.collection_provider import CollectionProvider
from mongorepo.exceptions import MongorepoDictNotFound


@overload
def provide_collection(repository: Any, collection: AsyncIOMotorCollection) -> None:
    ...


@overload
def provide_collection(repository: Any, collection: Collection[Any]) -> None:
    ...


def provide_collection(repository: Any, collection) -> None:
    """Provides collection to a mongorepo repository."""
    __mongorepo__ = getattr(repository, '__mongorepo__', None)
    if not __mongorepo__:
        raise MongorepoDictNotFound(
            message="Cannot provide collection to a repository that does not implement "
            f"{HasMongorepoDict.__name__} protocol. "
            "Recheck if the repository decorated with any mongorepo decorator",
        )
    provider = CollectionProvider(repository, collection)
    __mongorepo__['collection_provider'] = provider
