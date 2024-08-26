from dataclasses import asdict
from typing import Any, Callable, AsyncGenerator

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from mongorepo.utils import _get_converter, raise_exc
from mongorepo import DTO, exceptions


def _add_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    id_field: str | None = None,
) -> Callable:

    async def add(self, dto: DTO) -> DTO:
        await collection.insert_one(asdict(dto))
        return dto

    async def add_and_return_with_id(self, dto: DTO) -> DTO:
        object_id = ObjectId()
        dto.__dict__[id_field] = str(object_id)  # type: ignore
        await collection.insert_one({**asdict(dto), '_id': object_id})
        return dto

    if not id_field:
        return add
    return add_and_return_with_id


def _add_batch_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    id_field: str | None = None,
) -> Callable:

    async def add(self, dto_list: list[DTO]) -> None:
        await collection.insert_many(asdict(d) for d in dto_list)

    async def add_and_return_with_id(self, dto_list: list[DTO]) -> None:
        batch: list[dict[str, Any]] = []
        for dto in dto_list:
            object_id = ObjectId()
            dto.__dict__[id_field] = str(object_id)  # type: ignore  checked on 49-51 lines
            batch.append({**asdict(dto), '_id': object_id})
        await collection.insert_many(batch)

    if id_field is not None:
        return add
    return add_and_return_with_id


def _get_list_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    id_field: str | None = None,
):
    to_dto = _get_converter(dto_type, id_field=id_field)

    async def get_list(self, offset: int = 0, limit: int = 20) -> list[DTO]:
        cursor = collection.find().skip(offset).limit(limit)
        return [to_dto(dto_type, doc) async for doc in cursor]
    return get_list


def _get_all_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    id_field: str | None = None
) -> Callable:
    to_dto = _get_converter(dto_type, id_field=id_field)

    async def get_all(self, **filters: Any) -> AsyncGenerator[DTO, None]:
        cursor = collection.find(filters)
        async for dct in cursor:
            yield to_dto(dto_type, dct)
    return get_all


def _update_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    id_field: str | None = None
) -> Callable:
    to_dto = _get_converter(dto_type, id_field=id_field)

    async def update(self, dto: DTO, **filters: Any) -> DTO | None:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():
            if isinstance(value, (int, bool, float)):
                data['$set'][field] = value
            elif not field:
                continue
            else:
                data['$set'][field] = value
        doc: dict | None = await collection.find_one_and_update(
            filter=filters, update=data, return_document=True,
        )
        return to_dto(dto_type, doc) if doc else None
    return update


def _delete_method_async(dto_type: type[DTO], collection: AsyncIOMotorCollection) -> Callable:
    async def delete(self, **filters: Any) -> bool:
        deleted = await collection.find_one_and_delete(filters)
        return True if deleted else False
    return delete


def _get_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    id_field: str | None = None
) -> Callable:
    to_dto = _get_converter(dto_type, id_field=id_field)

    async def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        result = await collection.find_one(filters)
        return to_dto(dto_type, result) if result else None
    return get


def _update_field_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    id_field: str | None = None
) -> Callable:
    to_dto = _get_converter(dto_type, id_field=id_field)

    async def update_field(self, field_name: str, value: Any, **filters) -> DTO | None:
        if field_name not in dto_type.__dict__['__annotations__']:
            raise exceptions.MongoRepoException(
                message=f'{dto_type} does not have field "{field_name}"'
            )
        document = await collection.find_one_and_update(
            filter=filters, update={'$set': {field_name: value}}, return_document=True,
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return to_dto(dto_type, document)
    return update_field
