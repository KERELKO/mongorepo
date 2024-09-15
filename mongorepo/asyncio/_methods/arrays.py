from dataclasses import asdict, is_dataclass
from typing import Any, Callable

from motor.motor_asyncio import AsyncIOMotorCollection

from mongorepo.utils import _get_converter, _get_dataclass_fields, raise_exc
from mongorepo import DTO, exceptions
from mongorepo._base import _DTOField


def _get_list_of_field_values_method_async(
    dto_type: type[DTO], collection: AsyncIOMotorCollection, field_name: str,
) -> Callable:
    dataclass_fields = _get_dataclass_fields(dto_type=dto_type, only_dto_types=True)
    field_type = dataclass_fields.get(field_name, None)

    async def get_list_dto(
        self, offset: int, limit: int, **filters,
    ) -> list[_DTOField]:  # type: ignore
        document = await collection.find_one(
            filters, {field_name: {'$slice': [offset, limit]}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return [to_dto(field_type, d) for d in document[field_name]]

    async def get_list(self, offset: int, limit: int, **filters) -> list[Any]:
        document = await collection.find_one(
            filters, {field_name: {'$slice': [offset, limit]}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return document[field_name]

    if is_dataclass(field_type):
        to_dto = _get_converter(field_type)
        return get_list_dto
    return get_list


def _update_list_field_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    field_name: str,
    command: str = '$push',
) -> Callable:
    dataclass_fields = _get_dataclass_fields(dto_type=dto_type, only_dto_types=True)
    field_type = dataclass_fields.get(field_name, None)

    async def update_list(self, value: Any, **filters) -> None:
        value = asdict(value) if is_dataclass(field_type) else value
        document = await collection.update_one(
            filter=filters, update={command: {field_name: value}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
    return update_list


def _pop_list_method_async(
    dto_type: type[DTO],
    collection: AsyncIOMotorCollection,
    field_name: str,
) -> Callable:
    dataclass_fields = _get_dataclass_fields(dto_type=dto_type, only_dto_types=True)
    field_type = dataclass_fields.get(field_name, None)

    async def pop_list(self, **filters) -> Any | None:
        document = await collection.find_one_and_update(
            filter=filters, update={'$pop': {field_name: 1}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return document[field_name][-1] if document else None

    async def pop_list_dto(self, **filters) -> Any | None:
        document = await collection.find_one_and_update(
            filter=filters, update={'$pop': {field_name: 1}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return to_dto(field_type, document[field_name][-1]) if document else None

    if is_dataclass(field_type):
        to_dto = _get_converter(dataclass_fields[field_name])
        return pop_list_dto
    return pop_list
