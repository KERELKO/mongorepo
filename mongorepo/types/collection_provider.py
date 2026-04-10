from typing import Any, Generic

from mongorepo import exceptions

from .base import CollectionType


class CollectionProvider(Generic[CollectionType]):
    """Class that provides collections for mongorepo repositories."""

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

        # If no collection raise exception
        raise exceptions.NoCollectionException('Collection cannot be found')
