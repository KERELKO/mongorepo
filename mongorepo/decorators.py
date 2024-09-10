from typing import Annotated, Callable

from mongorepo.base import Access
from mongorepo.handlers import _handle_mongo_repository, _handle_implements


def mongo_repository(
    cls: type | None = None,
    add: bool = True,
    add_batch: bool = True,
    get: bool = True,
    get_all: bool = True,
    get_list: bool = True,
    update: bool = True,
    delete: bool = True,
    integer_fields: list[Annotated[str, 'field names']] | None = None,
    array_fields: list[Annotated[str, 'field names']] | None = None,
    method_access: Access | None = None,
) -> type | Callable:
    """
    ## Decorator for MongoDB repositories

    * decorated class must provide `Meta` class inside
    with variables "dto"(represent simple dataclass) and
    `collection` (represent mongo collection of type `Collection` from `pymongo` library)

    * You can also provide `index` field that can be just a string name of the field
    which you want to make index field or it can be instance of `mongorepo.Index`
    with extended settings

    * You can use `method_access` to make all methods
    private, protected or public (use `mongorepo.Access`)

    * Add `array_fields` to params to extend repository with methods
    that related to list fields in your dto type

    {field}__pop, {field}__list, {field}__remove, {field__append}

    * Add `integer_fields` to params to extend repository with methods
    that related to integer fields in your dto type

    increment_{field}, decrement_{field}

    ## Example

    ```
    @mongo_repository(delete=False)
    class MongoRepository:
        class Meta:
            dto = UserDTO
            collection: Collection = db["users"]
            index = mongorepo.Index(field="name")
            method_access = mongorepo.Access.PROTECTED

    r = MongoRepository()

    r.add(UserDTO(username="admin"))

    admin = r.get(username="admin")  # UserDTO(username="admin")

    ```

    """

    def wrapper(cls) -> type:
        return _handle_mongo_repository(
            cls=cls,
            add=add,
            update=update,
            get_all=get_all,
            get=get,
            get_list=get_list,
            delete=delete,
            add_batch=add_batch,
            integer_fields=integer_fields,
            array_fields=array_fields,
            method_access=method_access,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)


def implements(base_cls: type, **methods: str | Callable) -> Callable:
    """
    Decorator that allows to implement methods of `base_cls`
    you can specify them in `**methods`

    ### Decorator usage example:

    ```
    class A:
        def get_my_entity(self, id: str):
            ...

    @implements(A, get=A.get_my_entity)
    class MongoRepo:
        class Meta:
            dto = SimpleDTO
            collection = random_collection()

    my_entity = MongoRepo().get_my_entity(id="10")

    ```

    """
    def wrapper(cls) -> type:
        return _handle_implements(
            base_cls=base_cls,
            cls=cls,
            **methods,
        )
    return wrapper
