from typing import Any, Callable

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo.collection_provider import CollectionProvider


def use_collection[T](
    collection: AsyncIOMotorCollection | Collection[Any],
) -> Callable[[T], T]:
    """Decorator to bind a specific MongoDB collection to a repository class.

    This is useful when dynamically selecting a collection for repositories
    that are decorated with `mongorepo.repository`, `mongorepo.async_repository`,
    or `mongorepo.implement.implement`. It also works with repositories that
    inherit from `mongorepo.BaseMongoRepository` or `mongorepo.BaseAsyncMongoRepository`.

    ### Features:
    - Works with any class decorated using:
      - :class:`mongorepo.repository`
      - :class:`mongorepo.async_repository`
      - :class:`mongorepo.implement.implement`
    - Supports classes that inherit from:
      - :class:`mongorepo.BaseMongoRepository`
      - :class:`mongorepo.BaseAsyncMongoRepository`
    - Enables dynamic lookup of collections at runtime.

    ### Example:
    ```python
    from mongorepo import repository
    from my_project.database import my_collection

    # 1. Using the decorator on a repository class
    @use_collection(my_collection)
    @repository(add=True, get=True)
    class Repository:
        class Meta:
            dto = SimpleDTO

    # 2. Applying the decorator dynamically
    def provide_repository() -> Repository:
        return use_collection(my_collection)(Repository)()

    repo = provide_repository()
    ```

    """
    def wrapper(cls: T) -> T:
        provider = CollectionProvider(cls, collection)  # type: ignore
        if (__mongorepo__ := getattr(cls, '__mongorepo__', None)) is not None:
            __mongorepo__['collection_provider'] = provider  # type: ignore
        else:
            setattr(cls, '__mongorepo__', {'collection_provider': provider, 'methods': {}})
        return cls
    return wrapper
