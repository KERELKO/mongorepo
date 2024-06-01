from dataclasses import asdict
from typing import Any, Callable, Type, TypeVar

from bson import ObjectId
from pymongo.collection import Collection


TypeDTO = TypeVar('TypeDTO')


def mongo_repository_factory(
    cls: type | None = None,
    create: bool = True,
    get: bool = True,
) -> type:
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
        return _manage(cls=cls, create=create, get=get)

    if cls is None:
        return wrapper

    return wrapper(cls)


def _manage(cls, create: bool, get: bool) -> type:
    attributes = _get_repo_attributes(cls)
    dto = attributes['dto']
    collection = attributes['collection']
    if create:
        setattr(cls, 'create', _create(dto, collection=collection))
    if get:
        setattr(cls, 'get', _get(dto, collection=collection))
    return cls


def _get_repo_attributes(cls) -> dict[str, Any]:
    attributes = {}
    try:
        meta = cls.__dict__['Meta']
    except AttributeError as e:
        raise AttributeError('Decorated class does not have "Meta" class inside') from e
    try:
        dto: Type[TypeDTO] = meta.dto
        attributes['dto'] = dto
    except AttributeError as e:
        raise AttributeError('Decorated class does not have DTO type inside') from e
    try:
        collection: Collection = meta.collection
        attributes['collection'] = collection
    except AttributeError as e:
        raise AttributeError('Decorated class does not have "collection" inside') from e
    return attributes


def _create(dto: Type[TypeDTO], collection: Collection) -> Callable:
    def create(self, dto: TypeDTO) -> TypeDTO:
        collection.insert_one(asdict(dto))
        return dto
    return create


def _get(dto: Type[TypeDTO], collection: Collection) -> Callable:
    def get(self, oid: str) -> TypeDTO:
        result = collection.find_one({"_id": ObjectId(oid)})
        if not result:
            return None
        return dto(**result)
    return get
