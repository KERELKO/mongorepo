from dataclasses import asdict
from typing import Any, Callable, Iterable, Type, TypeVar

from pymongo.collection import Collection
from bson import ObjectId

from mongorepo.base import MongoDTO


DTO = TypeVar('DTO', bound=MongoDTO)


def _create_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def create(self, dto: DTO) -> DTO:
        collection.insert_one(asdict(dto))
        return dto
    return create


def _get_by_id_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def get_by_id(self, id: str | ObjectId) -> DTO | None:
        _id = ObjectId(id) if isinstance(id, str) else id
        result = collection.find_one({'_id': _id})
        if not result:
            return None
        return dto_type(**result)
    return get_by_id


def _get_all_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def get_all(self, **filters: dict[str, Any]) -> Iterable[DTO]:
        cursor = collection.find(filters)
        for dto in cursor:
            yield dto
    return get_all


def _update_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def update(self, dto: DTO) -> DTO:
        data = {'$set': asdict(dto)}
        _id = data['$set'].pop('_id')
        collection.find_one_and_update(filter={'_id': _id}, update=data)
        return dto
    return update


def _delete_by_id_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def delete_by_id(self, id: str) -> bool:
        deleted = collection.find_one_and_delete({'_id': ObjectId(id)})
        if deleted is not None:
            return True
        return False
    return delete_by_id


def _get_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def get(self, **filters) -> DTO | None:
        result = collection.find_one(filters)
        if not result:
            return None
        return dto_type(**result)
    return get
