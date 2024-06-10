from dataclasses import asdict
from typing import Any, Callable, Iterable, Type

from pymongo.collection import Collection

from mongorepo import DTO


def _add_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def add(self, dto: DTO) -> DTO:
        collection.insert_one(asdict(dto))
        return dto
    return add


def _get_all_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def get_all(self, **filters: Any) -> Iterable[DTO]:
        cursor = collection.find(filters)
        for dct in cursor:
            yield convert_to_dto(dto_type, dct)
    return get_all


def _update_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def update(self, dto: DTO, **filters: Any) -> DTO:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():
            if isinstance(value, (int, bool, float)):
                data['$set'][field] = value
            elif not value:
                continue
            else:
                data['$set'][field] = value
        collection.find_one_and_update(filter=filters, update=data)
        return dto
    return update


def _delete_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def delete(self, _id: str | None = None, **filters: Any) -> bool:
        if _id is not None:
            filters['_id'] = _id
        deleted = collection.find_one_and_delete(filters)
        if deleted is not None:
            return True
        return False
    return delete


def _get_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        if _id is not None:
            filters['_id'] = _id
        result = collection.find_one(filters)
        if not result:
            return None
        return convert_to_dto(dto_type, result)
    return get


def convert_to_dto(dto_type: Type[DTO], dct: dict[str, Any]) -> DTO:
    if '_id' in dto_type.__dict__['__annotations__']:
        return dto_type(**dct)
    dct.pop('_id')
    return dto_type(**dct)


METHOD_NAME__CALLABLE = {
    'get': _get_method,
    'add': _add_method,
    'update': _update_method,
    'delete': _delete_method,
    'get_all': _get_all_method,
}
