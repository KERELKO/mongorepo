from typing import Callable

from mongorepo.utils import _manage


def mongo_repository_factory(
    cls: type | None = None,
    create: bool = True,
    get_by_id: bool = True,
    get: bool = True,
    delete_by_id: bool = True,
    update: bool = True,
    get_all: bool = True,
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
        return _manage(
            cls=cls,
            create=create,
            get_by_id=get_by_id,
            delete_by_id=delete_by_id,
            update=update,
            get_all=get_all,
            get=get,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)
