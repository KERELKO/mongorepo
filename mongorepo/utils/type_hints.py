import datetime
import decimal
import inspect
import types
import uuid
from dataclasses import is_dataclass
from typing import Any, Callable, get_args, get_origin, get_type_hints

from mongorepo import exceptions
from mongorepo.types import Dataclass, Entity
from mongorepo.types.field_alias import FieldAlias


def is_entity_field(field_type: type, field_owner_type: type) -> bool:
    """Returns `True` if `field_type` is an entity field, `False` otherwise.

    If it cannot be
    determined by code - returns `True` as a fallback

    """

    primitives = frozenset([
        str, int, float, bool, bytes, type(None),
        datetime.datetime, datetime.date, datetime.time,
        uuid.UUID, decimal.Decimal,
    ])

    if field_type in primitives:
        return False

    # If it's not a type/class by this point (e.g., a string forward ref that wasn't resolved),
    # fail safely
    if not isinstance(field_type, type):
        return False

    if field_type is field_owner_type:
        return True

    if is_dataclass(field_type):
        return True

    return True


def get_first_arg(type_hint) -> Any:
    """Returns first argument of the type hint if it exists."""
    first_list_arg = get_args(type_hint)[0]
    if type(first_list_arg) is types.UnionType:
        first_list_arg = get_args(first_list_arg)[0]
    elif type(first_list_arg) is types.GenericAlias:
        first_list_arg = get_origin(first_list_arg)
    return first_list_arg


def get_entity_type_hints(entity: type) -> dict[str, Any]:
    type_hints: dict[str, Any] = {}

    for field_name, hint in get_type_hints(entity).items():
        if (org := get_origin(hint)) is list:
            first_left_arg = get_first_arg(hint)
            type_hints[field_name] = first_left_arg
        elif org is types.UnionType:
            type_hints[field_name] = get_args(hint)[0]
        else:
            type_hints[field_name] = hint

    return type_hints


def field_exists(field_name: str | FieldAlias, entity_type: type) -> bool:
    """Checks whether `field_name` is a field in `entity`"""
    for entity_field_type_hint in get_type_hints(entity_type).keys():
        if isinstance(field_name, str) and field_name == entity_field_type_hint:
            return True
        elif isinstance(field_name, FieldAlias) and field_name.name == entity_field_type_hint:
            return True
    return False


def has_entity_fields(entity_type: type[Dataclass]) -> bool:
    """Checks if entity type has nested entity fields."""
    type_hints = get_entity_type_hints(entity_type)
    for v in type_hints.values():
        if is_entity_field(v, entity_type):
            return True
    return False


def check_valid_field_type(field_name: str, entity_type: type[Entity], data_type: type) -> None:
    """Checks if provided `data_type` of `field_name` has the same type as a
    field in declared entity type."""
    field = entity_type.__annotations__.get(field_name, None)
    if field is None:
        raise exceptions.MongorepoException(
            message=f'{entity_type} does not have field "{field_name}"',
        )
    org = get_origin(field)
    if field == data_type or org is data_type:
        return
    elif type(org) is types.UnionType:
        union_args = get_args(org)
        if union_args[0] != data_type:
            raise exceptions.MongorepoException(
                message=f'Invalid type of the field "{field_name}", expected: {data_type}',
            )
    raise exceptions.MongorepoException(
        message=f'Invalid type of the field "{field_name}", expected: {data_type}',
    )


def get_function_default_values(func: Callable) -> dict[str, Any]:
    """Return default values for function parameters if any provided."""
    result = {}
    params = inspect.signature(func).parameters
    for param in params.values():
        if param.default is not inspect._empty:
            result[param.name] = param.default
    return result
