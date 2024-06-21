from typing import Callable, Annotated

from mongorepo.base import Access
from mongorepo.handlers import _handle_cls


def mongo_repository(
    cls: type | None = None,
    add: bool = True,
    get: bool = True,
    get_all: bool = True,
    get_list: bool = True,
    update: bool = True,
    delete: bool = True,
    update_field: bool = False,
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

    ### usage example:
    ```
    @mongo_repository(delete=False)
    class MongoRepository:
        class Meta:
            dto = UserDTO
            collection: Collection = db["users"]
            index = mongorepo.Index(field="name")
            method_access = mongorepo.Access.PROTECTED
    ```
    """

    def wrapper(cls) -> type:
        return _handle_cls(
            cls=cls,
            add=add,
            update=update,
            get_all=get_all,
            get=get,
            get_list=get_list,
            delete=delete,
            update_field=update_field,
            integer_fields=integer_fields,
            array_fields=array_fields,
            method_access=method_access,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)
