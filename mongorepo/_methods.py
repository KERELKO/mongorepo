from dataclasses import asdict
from typing import Any, Callable, Iterable, Type

from pymongo.collection import Collection

from mongorepo import DTO, exceptions


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
    def delete(self, **filters: Any) -> bool:
        deleted = collection.find_one_and_delete(filters)
        return True if deleted else False
    return delete


def _get_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def get(self, **filters: Any) -> DTO | None:
        result = collection.find_one(filters)
        return convert_to_dto(dto_type, result) if result else None
    return get


# TODO: add support + async support
def _replace_field_value_method(dto_type: Type[DTO], collection: Collection) -> Callable:
    def update_field(self, field_name: str, value: Any, **filters) -> DTO | None:
        if field_name not in dto_type.__dict__['__annotations']:
            raise exceptions.MongoRepoException(
                message=f'{dto_type} does have field "{field_name}"'
            )
        result = collection.find_one_and_update(filter=filters, update={field_name: value})
        return convert_to_dto(dto_type, result) if result else None
    return update_field


# TODO: add support + async support
def _update_integer_field_method(
    dto_type: Type[DTO], collection: Collection, field_name: str, weight: int = 1,
) -> Callable:
    def update_interger_field(self, **filters) -> DTO | None:
        document = collection.find_one_and_update(
            filter=filters, update={'$inc': {field_name: weight}},
        )
        return convert_to_dto(dto_type=dto_type, dct=document) if document else None
    return update_interger_field


# TODO: add support + async support
def _update_list_field_method(
    dto_type: Type[DTO], collection: Collection, field_name: str, command: str = '$push',
) -> Callable:
    def update_list(self, value: Any, **filters) -> Any:
        document = collection.find_one_and_update(
            filter=filters, update={command: {field_name: value}},
        )
        return convert_to_dto(dto_type=dto_type, dct=document) if document else None
    return update_list


def convert_to_dto(dto_type: Type[DTO], dct: dict[str, Any]) -> DTO:
    if '_id' in dto_type.__dict__['__annotations__']:
        return dto_type(**dct)
    dct.pop('_id')
    return dto_type(**dct)


METHOD_NAME__CALLABLE: dict[str, Callable] = {
    'get': _get_method,
    'add': _add_method,
    'update': _update_method,
    'delete': _delete_method,
    'get_all': _get_all_method,
}
