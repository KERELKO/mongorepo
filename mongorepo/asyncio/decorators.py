from typing import Callable

from mongorepo._base import Access
from mongorepo._handlers import _handle_async_mongo_repository


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
    array_fields: list[str] | None = None,
    method_access: Access | None = None,
    __methods__: bool = True,
) -> type | Callable:
    """## Async MongoDB repository decorator

    * decorated class must provide `Meta` class inside
    with variables "dto"(dataclass interface) and
    `collection` (motor collection: `AsyncIOMotorCollection`).

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

    incr__{field}, decr__{field}

    * __methods__: if `True` set class property `__methods__`
    that list all available methods including `mongorepo` methods, can be useful
    if you want to debug or see the signature of generated methods

    ### Example of __methods__ property
    ```
    @async_mongorepo_repository(get_list=True, update=True, __methods__=True)
    class A:
        ...
    print(A().__methods__)
    # get_list(self, offset: int = 0, limit: int = 20) -> list[~DTO]
    # update(self, dto: ~DTO, **filters: Any) -> Optional[~DTO]
    ```

    ## Decorator usage example

    ```
    @async_mongo_repository(method_access=mongorepo.Access.PROTECTED)
    class MongoRepository:
        class Meta:
            dto = ExampleDTO
            collection: AsyncIOMotorCollection = db["example"]
            index = mongorepo.Index(field="id_field")

    r = MongoRepository()

    await r.add(ExampleDTO(key="value"))

    example = await repo.get(key="value")  # ExampleDTO(key="value")

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
            array_fields=array_fields,
            method_access=method_access,
            __methods__=__methods__,
        )

    if cls is None:
        return wrapper

    return wrapper(cls)
