from dataclasses import is_dataclass
from functools import partial
from typing import Any, Callable

from mongorepo.types import Dataclass, Entity
from mongorepo.utils.type_hints import (
    get_dataclass_type_hints,
    has_dataclass_fields,
)


def _convert_to_dto(entity_type: type[Entity], dct: dict[str, Any]) -> Entity:
    """Converts document to entity, does not include mongodb `_id`"""
    dct.pop('_id') if dct.get('_id', None) else ...
    return entity_type(**dct)


def _convert_to_dto_with_id(
    id_field: str,
) -> Callable:
    """Converts document to entity, includes mongodb `_id` allows to set
    specific field where to store `_id`"""
    def wrapper(entity_type: type[Entity], dct: dict[str, Any]) -> Entity:
        dct[id_field] = str(dct.pop('_id'))
        return entity_type(**dct)
    return wrapper


def _nested_convert_to_dto[T: Dataclass](
    dataclass_type: type[T], data: dict[str, Any], id_field: str | None = None,
) -> T:
    def convert(
        data: dict[str, Any], dataclass_type: type[T], as_dataclass: bool = True,
    ) -> dict[str, Any] | T:
        type_hints = get_dataclass_type_hints(dataclass_type)
        result = {}
        for key, value in data.items():
            is_dtcls = is_dataclass(h := type_hints[key])

            if is_dtcls and isinstance(value, list):
                result[key] = [convert(v, h, True) for v in value]
            elif is_dtcls:
                result[key] = convert(value, h, True)  # type: ignore
            else:
                result[key] = value

        return dataclass_type(**result) if as_dataclass else result

    result = {}
    if id_field is not None:
        result[id_field] = str(data.pop('_id'))
    else:
        data.pop('_id') if data.get('_id', None) else ...

    result.update(convert(data, dataclass_type, False))  # type: ignore[arg-type]
    return dataclass_type(**result)


def get_converter(
    entity_type: type[Entity], id_field: str | None = None,
) -> Callable[[type[Entity], dict[str, Any]], Entity]:
    """Returns proper dataclass converter based on type hints of the dataclas.

    ## Usage example::

        from mongorepo import get_converter

        @dataclass
        class User:
            id: str
            username: str
            friends: list['User'] = field(default_factory=list)

        to_user = functools.partial(get_converter(User), User)  # just not to pass User every time

        dct = {
            'id': '1',
            'username': 'admin',
            'friends': [
                {'id': 2, 'username': 'bob', 'friends': []},
                {'id': 3, 'username': 'destroyer', 'friends': [
                        {'id': 4, 'username': 'top_1', 'friends': []}
                    ]
                }
            ]
        }
        user = to_user(dct)

        pprint.pprint(user)
        # User(id='1',
        #     username='admin',
        #     friends=[User(id=2, username='bob', friends=[]),
        #             User(id=3,
        #                 username='destroyer',
        #                 friends=[User(id=4, username='top_1', friends=[])])])

    """

    converter: Callable[[type[Entity], dict[str, Any]], Entity] | partial = _convert_to_dto
    r = has_dataclass_fields(entity_type=entity_type)
    if r:
        converter = partial(_nested_convert_to_dto, id_field=id_field)
    elif id_field is not None:
        converter = _convert_to_dto_with_id(id_field=id_field)
    return converter
