from typing import Any, Callable

from ._methods import (
    _get,
    _get_all,
    _get_by_id_method,
    _update_method,
    _create_method,
    _delete_by_id_method,
)


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


def _manage(
    cls,
    create: bool,
    get_by_id: bool,
    update: bool,
    delete_by_id: bool,
    get: bool,
    get_all: bool,
) -> type:
    attributes = _get_repo_attributes(cls)
    dto = attributes['dto']
    collection = attributes['collection']
    if create:
        setattr(cls, 'create', _create_method(dto, collection=collection))
    if get_by_id:
        setattr(cls, 'get_by_id', _get_by_id_method(dto, collection=collection))
    if update:
        setattr(cls, 'update', _update_method(dto, collection=collection))
    if delete_by_id:
        setattr(cls, 'delete_by_id', _delete_by_id_method(dto, collection=collection))
    if get:
        setattr(cls, 'get', _get(dto, collection=collection))
    if get_all:
        setattr(cls, 'get_all', _get_all(dto, collection=collection))
    return cls


def _get_repo_attributes(cls) -> dict[str, Any]:
    attributes = {}
    try:
        meta = cls.__dict__['Meta']
    except AttributeError as e:
        raise AttributeError('Decorated class does not have "Meta" class inside') from e
    try:
        dto = meta.dto
        attributes['dto'] = dto
    except AttributeError as e:
        raise AttributeError('Decorated class does not have DTO type inside') from e
    try:
        collection = meta.collection
        attributes['collection'] = collection
    except AttributeError as e:
        raise AttributeError('Decorated class does not have "collection" inside') from e
    return attributes
