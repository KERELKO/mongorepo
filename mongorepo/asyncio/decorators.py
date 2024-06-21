from typing import Callable

from mongorepo.base import Access
from mongorepo.handlers import _handle_cls_async


def async_mongo_repository(
    cls: type | None = None,
    add: bool = True,
    get: bool = True,
    get_list: bool = True,
    get_all: bool = True,
    update: bool = True,
    delete: bool = True,
    update_field: bool = False,
    integer_fields: list[str] | None = None,
    array_fields: list[str] | None = None,
    method_access: Access | None = None,
) -> type | Callable:
    """
    ## Async MongoDB repository decorator

    * decorated class must provide `Meta` class inside
    with variables "dto"(dataclass interface) and
    `collection` (motor collection: `AsyncIOMotorCollection`).

    * You can also provide `index` field that can be just a string name of the field
    which you want to make index field or it can be instance of `mongorepo.Index`
    with extended settings

    * You can use `method_access` to make all methods
    private, protected or public (use `mongorepo.Access`)

    ### usage example:
    ```
    @async_mongo_repository(method_access=mongorepo.Access.PROTECTED)
    class MongoRepository:
        class Meta:
            dto = UserDTO
            collection: AsyncIOMotorCollection = db["users"]
            index = mongorepo.Index(field="name")
    ```
    """

    def wrapper(cls) -> type:
        return _handle_cls_async(
            cls=cls,
            add=add,
            update=update,
            get_all=get_all,
            get_list=get_list,
            get=get,
            delete=delete,
            update_field=update_field,
            integer_fields=integer_fields,
            array_fields=array_fields,
            method_access=method_access,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)
