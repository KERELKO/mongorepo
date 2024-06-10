from dataclasses import Field, dataclass
from enum import Enum
from typing import Any, ClassVar, Iterable, Protocol, TypeVar


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DTO = TypeVar('DTO', bound=DataclassInstance)


def get_available_meta_attributes(list_names: bool = False) -> dict[str, str] | list[str]:
    attrs = {
        'index': 'creates index for a collection',
        'method_access': (
            'added methods will be private, '
            'protected or public, use mongorepo.base.Access'
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


class IMongoRepository(Protocol[DTO]):
    def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        raise NotImplementedError

    def get_all(self, **filters: Any) -> Iterable[DTO]:
        raise NotImplementedError

    def update(self, dto: DTO, **filter_: Any) -> DTO:
        raise NotImplementedError

    def delete(self, _id: str | None = None, **filters: Any) -> bool:
        raise NotImplementedError

    def create(self, dto: DTO) -> DTO:
        raise NotImplementedError
