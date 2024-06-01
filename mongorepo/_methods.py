from dataclasses import asdict
from typing import Any, Callable, Iterable, Type, TypeVar

from pymongo.collection import Collection
from bson import ObjectId

from .base import MongoDTO


DTO = TypeVar('DTO', bound=MongoDTO)


def _create_method(dto: Type[DTO], collection: Collection) -> Callable:
    def create(self, dto: DTO) -> DTO:
        collection.insert_one(asdict(dto))
        return dto
    return create


def _get_by_id_method(dto: Type[DTO], collection: Collection) -> Callable:
    def get_by_id(self, id: str) -> DTO | None:
        result = collection.find_one({'_id': ObjectId(id)})
        if not result:
            return None
        return dto(**result)
    return get_by_id


def _get_all(dto: Type[DTO], collection: Collection) -> Callable:
    def get_all(self, filters: dict[str, Any]) -> Iterable[DTO]:
        cursor = collection.find(filters)
        for dto in cursor:
            yield dto
    return get_all


def _update_method(dto: Type[DTO], collection: Collection) -> Callable:
    def update(self, find_condition: dict[str, Any], set_dict: dict[str, Any]) -> DTO:
        updated = collection.find_one_and_update(find_condition, set_dict)
        return dto(**updated)
    return update


def _delete_by_id_method(dto: Type[DTO], collection: Collection) -> Callable:
    def delete_by_id(self, id: str) -> bool:
        deleted = collection.find_one_and_delete({'_id': ObjectId(id)})
        if deleted is not None:
            return True
        return False
    return delete_by_id


def _get(dto: Type[DTO], collection: Collection) -> Callable:
    def get(self, key: str, value: Any) -> DTO | None:
        result = collection.find_one({key: value})
        if not result:
            return None
        return dto(**result)
    return get
