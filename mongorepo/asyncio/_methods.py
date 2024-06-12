from dataclasses import asdict
from typing import Any, Callable, Type, AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorCollection

from mongorepo.utils import convert_to_dto
from mongorepo import DTO, exceptions


def _add_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def add(self, dto: DTO) -> DTO:
        await collection.insert_one(asdict(dto))
        return dto
    return add


def _get_all_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def get_all(self, **filters: Any) -> AsyncGenerator[DTO, None]:
        cursor = collection.find(filters)
        async for dct in cursor:
            yield convert_to_dto(dto_type, dct)
    return get_all


def _update_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def update(self, dto: DTO, **filters: Any) -> DTO:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():
            if isinstance(value, (int, bool, float)):
                data['$set'][field] = value
            elif not field:
                continue
            else:
                data['$set'][field] = value
        await collection.find_one_and_update(filter=filters, update=data)
        return dto
    return update


def _delete_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def delete(self, **filters: Any) -> bool:
        deleted = await collection.find_one_and_delete(filters)
        return True if deleted else False
    return delete


def _get_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        result = await collection.find_one(filters)
        return convert_to_dto(dto_type, result) if result else None
    return get


def _update_field_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def update_field(self, field_name: str, value: Any, **filters) -> DTO | None:
        if field_name not in dto_type.__dict__['__annotations__']:
            raise exceptions.MongoRepoException(
                message=f'{dto_type} does have field "{field_name}"'
            )
        result = await collection.find_one_and_update(
            filter=filters, update={'$set': {field_name: value}}, return_document=True,
        )
        return convert_to_dto(dto_type, result) if result else None
    return update_field


def _update_integer_field_method_async(
    dto_type: Type[DTO], collection: AsyncIOMotorCollection, field_name: str, _weight: int = 1,
) -> Callable:
    async def update_interger_field(self, weight: int | None = None, **filters) -> DTO | None:
        w = weight if weight is not None else _weight
        document = await collection.find_one_and_update(
            filter=filters, update={'$inc': {field_name: w}}, return_document=True
        )
        return convert_to_dto(dto_type=dto_type, dct=document) if document else None
    return update_interger_field


def _update_list_field_method_async(
    dto_type: Type[DTO],
    collection: AsyncIOMotorCollection,
    field_name: str,
    command: str = '$push',
) -> Callable:
    async def update_list(self, value: Any, **filters) -> Any:
        document = await collection.find_one_and_update(
            filter=filters, update={command: {field_name: value}}, return_document=True
        )
        return convert_to_dto(dto_type=dto_type, dct=document) if document else None
    return update_list


def _pop_list_method_async(
    dto_type: Type[DTO],
    collection: AsyncIOMotorCollection,
    field_name: str,
) -> Callable:
    async def pop_list(self, **filters) -> Any | None:
        document = await collection.find_one_and_update(
            filter=filters, update={'$pop': {field_name: 1}},
        )
        return document[field_name][-1] if document else None
    return pop_list


METHOD_NAME__CALLABLE: dict[str, Callable] = {
    'get': _get_method_async,
    'add': _add_method_async,
    'update': _update_method_async,
    'delete': _delete_method_async,
    'get_all': _get_all_method_async,
    'update_field': _update_field_method_async,
    'update_list': _update_list_field_method_async,
    'pop': _pop_list_method_async,
    'update_integer': _update_integer_field_method_async,
}
