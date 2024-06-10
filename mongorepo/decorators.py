from typing import Callable

from mongorepo.subst import substitute_class_methods
from mongorepo.handlers import _handle_cls


def mongo_repository(
    cls: type | None = None,
    add: bool = True,
    get: bool = True,
    get_all: bool = True,
    update: bool = True,
    delete: bool = True,
    update_field: bool = False,
    integer_fields: list[str] | None = None,
    array_fields: list[str] | None = None,
) -> type | Callable:
    """
    ## Decorator for mongo repositories

    * decorated class must provide `Meta` class inside
    with variables "dto"(represent simple dataclass) and
    `collection` (represent mongo collection of type `Collection` from `pymongo` library)

    * You can also provide `index` field that can be just a string name of the field
    which you want to make index field or it can be instance of `mongorepo.Index`
    with extended settings

    * Use `method_access` in Meta class of the decorated class to make all methods
    private, protected or public (use mongorepo.Access enum)

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
            delete=delete,
            update_field=update_field,
            integer_fields=integer_fields,
            array_fields=array_fields,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)


def substitute(source_cls: type) -> type | Callable:
    def wrapper(target_cls) -> type:
        return substitute_class_methods(
            target_cls=target_cls,
            source_cls=source_cls
        )

    return wrapper
