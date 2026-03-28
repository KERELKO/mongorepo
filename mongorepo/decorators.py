from typing import Callable, Iterable

from mongorepo._handlers import (
    _handle_async_mongo_repository,
    _handle_mongo_repository,
)
from mongorepo.types import RepositoryConfig


def mongo_repository(
    config: RepositoryConfig,
    add: bool = True,
    add_batch: bool = True,
    get: bool = True,
    get_all: bool = True,
    get_list: bool = True,
    update: bool = True,
    delete: bool = True,
    integer_fields: Iterable[str] | None = None,
    list_fields: Iterable[str] | None = None,
) -> type | Callable:
    """Decorator for creating a synchronous MongoDB repository.

    This decorator enhances a class with common repository methods for handling
    MongoDB collections using `pymongo`'s `Collection`.

    ## Parameters:
    - `add` (bool): Enables the `add` method to insert a document (default: True).
    - `add_batch` (bool): Enables batch insertion of multiple documents (default: True).
    - `get` (bool): Enables retrieval of a single document by filters (default: True).
    - `get_list` (bool): Enables retrieval of multiple documents with pagination (default: True).
    - `get_all` (bool): Enables retrieval of all documents (default: True).
    - `update` (bool): Enables document updates (default: True).
    - `delete` (bool): Enables document deletion (default: True).
    - `integer_fields` (Iterable[str], optional): Fields that support atomic increment/decrement:
      - `increment_{field}`: Increments the field.
      - `decrement_{field}`: Decrements the field.
    - `list_fields` (Iterable[str], optional): Fields treated as lists, enabling:
      - `{field}__append`: Appends an item to the list.
      - `{field}__remove`: Removes an item from the list.
      - `{field}__pop`: Pops an item from the list.
      - `{field}__list`: Retrieves the list field values.

    ## Example Usage:
    ```python
    @mongo_repository(config=RepositoryConfig(entity_type=User, collection=db["users"]))
    class MongoRepository:
        ...

    repo = MongoRepository()

    repo.add(User(username="admin"))

    admin = repo.get(username="admin")  # User(username="admin")
    ```

    """

    def wrapper[T](cls: type[T]) -> type[T]:
        return _handle_mongo_repository(
            cls=cls,
            config=config,
            add=add,
            add_batch=add_batch,
            get_all=get_all,
            get_list=get_list,
            delete=delete,
            update=update,
            get=get,
            integer_fields=integer_fields,
            list_fields=list_fields,
        )

    return wrapper


def async_mongo_repository(
    config: RepositoryConfig,
    add: bool = True,
    add_batch: bool = True,
    get: bool = True,
    get_list: bool = True,
    get_all: bool = True,
    update: bool = True,
    delete: bool = True,
    integer_fields: list[str] | None = None,
    list_fields: list[str] | None = None,
) -> type | Callable:
    """Decorator for creating an asynchronous MongoDB repository.

    This decorator enhances a class with common repository methods for handling
    MongoDB collections using `motor`'s `AsyncIOMotorCollection`.

    ## Parameters:
    - `add` (bool): Enables the `add` method to insert a document (default: True).
    - `add_batch` (bool): Enables batch insertion of multiple documents (default: True).
    - `get` (bool): Enables retrieval of a single document by filters (default: True).
    - `get_list` (bool): Enables retrieval of multiple documents with pagination (default: True).
    - `get_all` (bool): Enables retrieval of all documents (default: True).
    - `update` (bool): Enables document updates (default: True).
    - `delete` (bool): Enables document deletion (default: True).
    - `integer_fields` (list[str], optional): Fields that support atomic increment/decrement:
      - `incr__{field}`: Increments the field.
      - `decr__{field}`: Decrements the field.
    - `list_fields` (list[str], optional): Fields treated as lists, enabling:
      - `{field}__append`: Appends an item to the list.
      - `{field}__remove`: Removes an item from the list.
      - `{field}__pop`: Pops an item from the list.
      - `{field}__list`: Retrieves the list field values.

    ## Example Usage:
    ```python
    @mongo_repository(config=RepositoryConfig(entity_type=User, collection=db["users"]))
    class MongoRepository:
        ...

    repo = MongoRepository()

    await repo.add(User(username="admin"))

    admin = await repo.get(username="admin")  # User(username="admin")
    ```

    """
    def wrapper(cls) -> type:
        return _handle_async_mongo_repository(
            cls=cls,
            config=config,
            add=add,
            update=update,
            get_all=get_all,
            get_list=get_list,
            get=get,
            delete=delete,
            add_batch=add_batch,
            integer_fields=integer_fields,
            list_fields=list_fields,
        )

    return wrapper
