from dataclasses import asdict
from typing import Any, Callable, Iterable, Type

from pymongo.collection import Collection
from bson import ObjectId

from mongorepo.base import DTO


def _create_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def create(self, dto: DTO) -> DTO:
        collection.insert_one(asdict(dto))  # type: ignore
        return dto
    return create


def _get_all_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def get_all(self, **filters: dict[str, Any]) -> Iterable[DTO]:
        cursor = collection.find(filters)
        for dto in cursor:
            yield dto
    return get_all


def _update_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def update(self, dto: DTO, **filter) -> DTO:
        data = {'$set': {}}
        for field, value in asdict(dto).items():  # type: ignore
            if isinstance(value, (int, bool)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        collection.find_one_and_update(filter=filter, update=data)
        return dto
    return update


def _delete_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def delete(self, _id: str | None = None, **filters) -> bool:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        deleted = collection.find_one_and_delete(filters)
        if deleted is not None:
            return True
        return False
    return delete


def _get_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def get(self, _id: str | None = None, **filters) -> DTO | None:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        result = collection.find_one(filters)
        if not result:
            return None
        result.pop('_id')
        return dto_type(**result)
    return get
