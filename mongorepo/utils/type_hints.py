import inspect
import types
from dataclasses import is_dataclass
from typing import Any, Callable, get_args, get_origin, get_type_hints

from mongorepo import exceptions
from mongorepo.types import Dataclass, Entity


def get_first_arg(type_hint) -> Any:
    """Returns first argument of the type hint if it exists."""
    first_list_arg = get_args(type_hint)[0]
    if type(first_list_arg) is types.UnionType:
        first_list_arg = get_args(first_list_arg)[0]
    elif type(first_list_arg) is types.GenericAlias:
        first_list_arg = get_origin(first_list_arg)
    return first_list_arg


def get_dataclass_type_hints(dataclass: type[Dataclass]) -> dict[str, Any]:
    type_hints: dict[str, Any] = {}

    for field_name, hint in get_type_hints(dataclass).items():
        if is_dataclass(hint):
            type_hints[field_name] = hint
        elif (org := get_origin(hint)) is list:
            first_left_arg = get_first_arg(hint)
            type_hints[field_name] = first_left_arg
        elif org is types.UnionType:
            type_hints[field_name] = get_args(hint)[0]
        else:
            type_hints[field_name] = hint

    return type_hints


def has_dataclass_fields(entity_type: type[Entity]) -> bool:
    """Checks if entity type has nested dataclass fields."""
    type_hints = get_dataclass_type_hints(entity_type)
    for v in type_hints.values():
        if is_dataclass(v):
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
