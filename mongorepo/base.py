from dataclasses import Field, dataclass
from enum import Enum
from typing import Any, ClassVar, Protocol, TypeVar


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DTO = TypeVar('DTO', bound=DataclassInstance)


def get_available_meta_attributes(list_names: bool = False) -> dict[str, str] | list[str]:
    attrs = {
        'index': 'creates index for a collection',
        'method_access': (
            'added methods will be private, '
            'protected or public, use mongorepo.Access'
        ),
        'dto': 'sets default dto for repository, repository saves data in the format of the dto',
        'collection': 'sets default collection for repository',
        'substitute': (
            'substitutes methods of mongorepo decorator or class with provided or inherited class'
        ),
    }
    if list_names:
        return list(attrs.keys())
    return attrs


def get_available_repository_methods(list_names: bool = False) -> dict[str, str] | list[str]:
    methods = {
        'add': 'add document to a collection, collection stores it in dto format, params: dto: DTO',
        'delete': 'delete document from a collection, params: _id: str | None, **filters: Any',
        'update': (
            'update document in a collection takes dto as parameter, '
            'if no value in dto(except: float, int, bool) skips it'
        ),
        'get': 'retrieve a document from a collection, params: _id: str | None, **filters: Any',
        'get_all': 'retrive all documents of the same type(dto type), params: **filters: Any',
    }
    if list_names:
        return list(methods.keys())
    return methods


@dataclass(repr=False, slots=True, eq=False)
class Index:
    field: str
    name: str | None = None
    desc: bool = True
    unique: bool = False


class Access(int, Enum):
    PUBLIC = 0
    PROTECTED = 1
    PRIVATE = 2
