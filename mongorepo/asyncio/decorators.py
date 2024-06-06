from typing import Callable

from mongorepo.asyncio.utils import _handle_cls_async


def async_mongo_repository(
    cls: type | None = None,
    add: bool = True,
    get: bool = True,
    get_all: bool = True,
    update: bool = True,
    delete: bool = True,
) -> type | Callable:
    """
    ## MongoDB repository factory, use as decorator

    * decorated class must provide `Meta` class inside
    with variables "dto"(dataclass interface) and
    `collection` (motor collection: `AsyncIOMotorCollection`).

    #### NOTE: dto can also be defined in generic class type hints

    * You can also provide `index` field that can be just a string name of the field
    which you want to make index field or it can be instance of `mongorepo.base.Index`
    with extended settings
    * `method_access` to make all methods private, protected or public
    (use mongorepo.base.Access class)

    ### usage example:
    ```
    @async_mongo_repository
    class MongoRepository[UserDTO]:
        class Meta:
            collection: AsyncIOMotorCollection = db["users"]
            index = mongorepo.base.Index(field="name")
            method_access = mongorepo.base.Access.PROTECTED
    ```
    """

    def wrapper(cls) -> type:
        return _handle_cls_async(
            cls=cls,
            add=add,
            update=update,
            get_all=get_all,
            get=get,
            delete=delete,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)
