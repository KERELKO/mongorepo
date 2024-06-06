from typing import Callable

from mongorepo.utils import _handle_cls, _handle_cls_async


def mongo_repository_factory(
    cls: type | None = None,
    add: bool = True,
    get: bool = True,
    get_all: bool = True,
    update: bool = True,
    delete: bool = True,
    is_async: bool = False,
) -> type | Callable:
    """
    ## MongoDB repository factory, use as decorator

    * decorated class must provide `Meta` class inside
    with variables "dto"(represent simple dataclass) and
    `collection` (represent mongo collection of type `Collection` from `pymongo` library
    or async collection from motor: `AsyncIOMotorCollection` if is_async=True).

    * You can also provide `index` field that can be just a string name of the field
    which you want to make index field or it can be instance of `mongorepo.base.Index`
    with extended settings

    ### If is_async=True then all added methods will be asynchronous

    ### usage example:
    ```
    @mongo_repository_factory(is_async=True)
    class MongoRepository:
        class Meta:
            dto = UserDTO
            collection: Collection = db["users"]
            index = mongorepo.base.Index(field="name")
            method_access = mongorepo.base.Access.PROTECTED
    ```
    """

    def wrapper(cls) -> type:
        if is_async:
            return _handle_cls_async(
                cls=cls,
                add=add,
                update=update,
                get_all=get_all,
                get=get,
                delete=delete,
            )
        else:
            return _handle_cls(
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
