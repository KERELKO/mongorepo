from dataclasses import asdict
from typing import Any, Callable, Type, AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from mongorepo._methods import convert_to_dto
from mongorepo.base import DTO


def _create_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def create(self, dto: DTO) -> DTO:
        await collection.insert_one(asdict(dto))  # type: ignore
        return dto
    return create


def _get_all_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def get_all(self, **filters: Any) -> AsyncGenerator[DTO, None]:
        cursor = collection.find(filters)
        async for dct in cursor:
            yield convert_to_dto(dto_type, dct)  # type: ignore
    return get_all


def _update_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def update(self, dto: DTO, **filters: Any) -> DTO:
        data = {'$set': {}}
        for field, value in asdict(dto).items():  # type: ignore
            if isinstance(value, (int, bool)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        await collection.find_one_and_update(filter=filters, update=data)
        return dto
    return update


def _delete_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def delete(self, _id: str | None = None, **filters: Any) -> bool:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        deleted = await collection.find_one_and_delete(filters)
        if deleted is not None:
            return True
        return False
    return delete


def _get_method_async(dto_type: Type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        result = await collection.find_one(filters)
        if not result:
            return None
        return convert_to_dto(dto_type, result)  # type: ignore
    return get
