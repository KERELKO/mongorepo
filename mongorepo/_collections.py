import typing as t

from mongorepo import exceptions

from ._base import AsyncIOMotorCollection, Collection
from .utils import _get_collection_from_object, _get_meta

C = t.TypeVar('C', AsyncIOMotorCollection, Collection[t.Any])

COLLECTION_PROVIDER: t.Final[str] = '_mongorepo_collection_provider'


class CollectionProvider(t.Generic[C]):
    """Descriptor to get mongo collection."""

    def __init__(self, collection: C | None = None):
        self.collection: C | None = collection

    def __get__(self, obj: object, owner: type) -> C:
        # First check if collection already provided
        if self.collection is not None:
            return self.collection

        # Check if collection present in object attributes
        collection: C = _get_collection_from_object(obj)  # type: ignore
        if collection is not None:
            self.collection = collection
            return collection

        # Check if collection in Meta class
        meta = _get_meta(owner)
        if (c := meta.get('collection', None)) is not None:
            if not isinstance(c, (AsyncIOMotorCollection, Collection)):
                raise exceptions.NoCollectionException
            self.collection = c
            return c

        # If no collection raise exception
        raise exceptions.NoCollectionException('Collection cannot be found', with_meta=False)


class HasCollectionProvider(t.Protocol):
    _mongorepo_collection_provider: CollectionProvider


def use_collection[T: type](
    collection: AsyncIOMotorCollection | Collection[t.Any],
) -> t.Callable[[T], T]:
    """
    Simple decorator to make mongorepo use specific collection,
    useful for dynamic look up of collection

    ```
    # 1. Valid
    # @use_collection(my_collection)
    @mongorepo.repository(add=True, get=True)
    # 2. Valid
    # @use_collection(my_collection)
    class Repository:
        class Meta:
            dto = SimpleDTO

    def provide_repository() -> Repository:
        # 3. Valid
        return use_collection(my_collection)(Repository)()

    repo = provide_repository()
    ```
    """
    def wrapper(cls: T) -> T:
        setattr(cls, COLLECTION_PROVIDER, CollectionProvider(collection))  # type: ignore
        return cls
    return wrapper
