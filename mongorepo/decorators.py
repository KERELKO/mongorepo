from typing import Callable, Iterable

from mongorepo._base import Access
from mongorepo._handlers import (
    _handle_async_mongo_repository,
    _handle_mongo_repository,
)


def mongo_repository(
    cls: type | None = None,
    add: bool = True,
    add_batch: bool = True,
    get: bool = True,
    get_all: bool = True,
    get_list: bool = True,
    update: bool = True,
    delete: bool = True,
    integer_fields: Iterable[str] | None = None,
    list_fields: Iterable[str] | None = None,
    method_access: Access | None = None,
) -> type | Callable:
    """Decorator for creating a synchronous MongoDB repository.

    This decorator enhances a class with common repository methods for handling
    MongoDB collections using `pymongo`'s `Collection`.

    ## Requirements:
    The decorated class must define a nested `Meta` class with:
    - `dto`: A dataclass representing the document schema.
    - `collection`: An instance of `Collection` from `pymongo`.
    - `index` (optional): Either:
      - A string representing the indexed field.
      - An instance of `mongorepo.Index` for advanced indexing options.
    - `method_access` (optional): Specifies the access level for repository methods
      using `mongorepo.Access`.

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
    - `method_access` (`mongorepo.Access`, optional): Defines method access level
      (`PUBLIC`, `PROTECTED`, `PRIVATE`).

    ## Example Usage:
    ```python
    @mongo_repository(delete=False)
    class MongoRepository:
        class Meta:
            dto = UserDTO
            collection: Collection = db["users"]
            index = mongorepo.Index(field="name")
            method_access = mongorepo.Access.PUBLIC

    repo = MongoRepository()

    repo.add(UserDTO(username="admin"))

    admin = repo.get(username="admin")  # UserDTO(username="admin")
    ```

    """

    def wrapper(cls) -> type:
        return _handle_mongo_repository(
            cls=cls,
            add=add,
            add_batch=add_batch,
            get_all=get_all,
            get_list=get_list,
            delete=delete,
            update=update,
            get=get,
            integer_fields=integer_fields,
            list_fields=list_fields,
            method_access=method_access,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)


def async_mongo_repository(
    cls: type | None = None,
    add: bool = True,
    add_batch: bool = True,
    get: bool = True,
    get_list: bool = True,
    get_all: bool = True,
    update: bool = True,
    delete: bool = True,
    integer_fields: list[str] | None = None,
    list_fields: list[str] | None = None,
    method_access: Access | None = None,
) -> type | Callable:
    """Decorator for creating an asynchronous MongoDB repository.

    This decorator enhances a class with common repository methods for handling
    MongoDB collections using `motor`'s `AsyncIOMotorCollection`.

    ## Requirements:
    The decorated class must define a nested `Meta` class with:
    - `dto`: A dataclass representing the document schema.
    - `collection`: An instance of `AsyncIOMotorCollection`.
    - `index` (optional): Either:
      - A string representing the indexed field.
      - An instance of `mongorepo.Index` for advanced indexing options.
    - `method_access` (optional): Specifies the access level for repository methods
      using `mongorepo.Access`.

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
    - `method_access` (`mongorepo.Access`, optional): Defines method access level
      (`PUBLIC`, `PROTECTED`, `PRIVATE`).

    ## Example Usage:
    ```python
    @async_mongo_repository(get_all=True, update=True)
    class MongoRepository:
        class Meta:
            dto = ExampleDTO
            collection: AsyncIOMotorCollection = db["example"]
            index = mongorepo.Index(field="id_field")
            method_access = mongorepo.Access.PUBLIC

    repo = MongoRepository()

    await repo.add(ExampleDTO(key="value"))

    example = await repo.get(key="value")  # Returns ExampleDTO(key="value")
    ```

    """
    def wrapper(cls) -> type:
        return _handle_async_mongo_repository(
            cls=cls,
            add=add,
            update=update,
            get_all=get_all,
            get_list=get_list,
            get=get,
            delete=delete,
            add_batch=add_batch,
            integer_fields=integer_fields,
            list_fields=list_fields,
            method_access=method_access,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)
