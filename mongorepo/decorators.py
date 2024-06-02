from typing import Callable

from mongorepo.utils import _handle_cls


def mongo_repository_factory(
    cls: type | None = None,
    create: bool = True,
    get: bool = True,
    get_all: bool = True,
    update: bool = True,
    delete: bool = True,
) -> type | Callable:
    """
    MongoDB repository factory, use as decorator,
    decorated class must provide "Meta" class inside
    with variables "dto"(represent simple dataclass) and
    "collection" (represent mongo collection of type "Collection" from pymongo library)

    ### example:
    ```
    class MongoRepository:
        class Meta:
            dto = UserDTO
            collection: Collection = db["users"]
    ```
    """

    def wrapper(cls) -> type:
        return _handle_cls(
            cls=cls,
            create=create,
            update=update,
            get_all=get_all,
            get=get,
            delete=delete,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)
