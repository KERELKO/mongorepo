from dataclasses import asdict, is_dataclass
from typing import Any, Callable

from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import DTO, _DTOField
from mongorepo.queries import Operation
from mongorepo.utils import _get_converter, _get_dataclass_fields, raise_exc


def _update_list_field_method(
    dto_type: type[DTO], collection: Collection, field_name: str, command: Operation = '$push',
) -> Callable:
    dataclass_fields = _get_dataclass_fields(dto_type=dto_type, only_dto_types=True)
    field_type = dataclass_fields.get(field_name, None)

    def update_list(self, value: Any, **filters) -> None:
        value = value if not is_dataclass(field_type) else asdict(value)
        doc = collection.update_one(
            filter=filters, update={command: {field_name: value}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not doc else ...
    return update_list


def _get_list_of_field_values_method(
    dto_type: type[DTO], collection: Collection, field_name: str,
) -> Callable:
    dataclass_fields = _get_dataclass_fields(dto_type=dto_type, only_dto_types=True)
    field_type = dataclass_fields.get(field_name, None)

    def get_list_dto(
        self, offset: int = 0, limit: int = 20, **filters,
    ) -> list[_DTOField]:  # type: ignore
        document = collection.find_one(
            filters, {field_name: {'$slice': [offset, limit]}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return [to_dto(field_type, d) for d in document[field_name]]  # type: ignore

    def get_list(
        self, offset: int, limit: int, **filters,
    ) -> list[Any]:
        document = collection.find_one(
            filters, {field_name: {'$slice': [offset, limit]}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return document[field_name]  # type: ignore

    if is_dataclass(field_type):
        to_dto = _get_converter(dataclass_fields[field_name])
        return get_list_dto
    return get_list


def _pop_list_method(dto_type: type[DTO], collection: Collection, field_name: str) -> Callable:
    dataclass_fields = _get_dataclass_fields(dto_type=dto_type, only_dto_types=True)
    field_type = dataclass_fields.get(field_name, None)

    def pop_list(self, **filters) -> Any:
        document = collection.find_one_and_update(
            filter=filters, update={'$pop': {field_name: 1}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return document[field_name][-1]

    def pop_list_dto(self, **filters) -> Any:
        document = collection.find_one_and_update(
            filter=filters, update={'$pop': {field_name: 1}},
        )
        raise_exc(exceptions.NotFoundException(**filters)) if not document else ...
        return to_dto(field_type, document[field_name][-1])

    if is_dataclass(field_type):
        to_dto = _get_converter(dataclass_fields[field_name])
        return pop_list_dto
    return pop_list
