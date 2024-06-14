from dataclasses import is_dataclass
from typing import Any, Callable, Type, Union, get_args, get_origin

import pymongo
from pymongo.collection import Collection

from mongorepo import DTO, Access, Index
from mongorepo import exceptions


def _get_collection_and_dto(cls: type, raise_exceptions: bool = True) -> dict[str, Any]:
    """Collect "dto" and "collection" attributes from `Meta` class"""
    attributes: dict[str, Any] = {}
    meta = get_meta(cls)
    try:
        dto = meta.dto
        attributes['dto'] = dto
    except AttributeError as e:
        if raise_exceptions:
            raise exceptions.NoDTOTypeException from e
        else:
            attributes['dto'] = None
    try:
        collection = meta.collection
        attributes['collection'] = collection
    except AttributeError as e:
        if raise_exceptions:
            raise exceptions.NoCollectionException from e
        else:
            attributes['collection'] = None

    return attributes


def _get_meta_attributes(cls, raise_exceptions: bool = True) -> dict[str, Any]:
    """
    Collect all available attributes from `Meta` class
    * use `mongorepo.get_available_meta_attributes` to get all available `Meta` attributes
    """
    attributes: dict[str, Any] = _get_collection_and_dto(
        cls=cls, raise_exceptions=raise_exceptions,
    )
    meta = get_meta(cls)

    index: Index | str | None = getattr(meta, 'index', None)
    attributes['index'] = index

    method_access: Access | None = getattr(meta, 'method_access', None)
    attributes['method_access'] = method_access

    substitute: dict[str, str] | None = getattr(meta, 'substitute', None)
    attributes['substitute'] = substitute

    id_field: str | None = getattr(meta, 'id_field', None)
    attributes['id_field'] = id_field

    return attributes


def get_meta(cls: type) -> Any:
    """
    Tries to get `Meta` class for the class or raises an exception
    """
    try:
        meta = cls.__dict__['Meta']
    except (AttributeError, KeyError) as e:
        raise exceptions.NoMetaException from e
    if not isinstance(meta, type):
        raise exceptions.NoMetaException
    return meta


def get_dto_type_hints(dto: Type[DTO] | DTO) -> dict[str, Any]:
    """Returns dictionary of fields' type hints for a dataclass or dataclass instance"""
    default_values = {}
    for field_name, value in dto.__annotations__.items():
        origin = get_origin(value)
        if isinstance(value, type):
            default_values[field_name] = value
        elif origin is list:
            default_values[field_name] = origin
        elif origin is Union:
            args = get_args(value)
            default_values[field_name] = get_origin(args[0])
    return default_values


def create_index(index: Index | str, collection: Collection) -> None:
    """
    ### Creates an index for the collection
    * index parameter can be string or `mongorepo.Index`
    * If index is string, create standard mongodb index
    * If it's `mongorepo.Index` creates index with user's settings
    """
    if isinstance(index, str):
        collection.create_index(index)
        return
    index_name = f'index_{index.field}'
    if index.name:
        index_name = index.name
    direction = pymongo.DESCENDING if index.desc else pymongo.ASCENDING
    collection.create_index(
        [(index.field, direction)],
        name=index_name,
        unique=index.unique,
    )


def get_prefix(access: Access | None, cls: type | None = None) -> str:
    """
    Returns string prefix according to Access value,
    * it can be `'_'`, `'__'`, `_{cls.__name__}__` or `''`
    """
    match access:
        case Access.PRIVATE:
            prefix = f'_{cls.__name__}__' if cls else '__'
        case Access.PROTECTED:
            prefix = '_'
        case Access.PUBLIC | None:
            prefix = ''
    return prefix


def _get_dto_from_origin(cls: type) -> Any:
    """
    Tries to get "dto" from origin of the class or raises an exception
    ```
    class A[UserDTO]: ...
    _get_dto_from_origin(A)
    UserDTO
    ```
    """
    try:
        if not hasattr(cls, '__orig_bases__'):
            raise exceptions.NoDTOTypeException
        dto: type = get_args(cls.__orig_bases__[0])[0]
    except IndexError:
        raise exceptions.NoDTOTypeException
    if dto is DTO:
        raise exceptions.NoDTOTypeException
    if not is_dataclass(dto):
        raise exceptions.NotDataClass

    return dto


def is_immutable(obj: Any) -> bool:
    """Check if object is immutable"""
    try:
        hash(obj)
    except TypeError:
        return False
    return True


def convert_to_dto(dto_type: Type[DTO], dct: dict[str, Any]) -> DTO:
    """
    Converts document to dto, does not include mongodb `_id`
    """
    dct.pop('_id')
    return dto_type(**dct)


def convert_to_dto_with_id(
    id_field: str | None = None,
) -> Callable:
    """
    Converts document to dto,
    icludes mongodb `_id` allows to set specific field where to store `_id`
    """
    def wrapper(dto_type: Type[DTO], dct: dict[str, Any]) -> DTO:
        if not id_field:
            return dto_type(**dct)
        dct[id_field] = str(dct['_id'])
        dct.pop('_id')
        return dto_type(**dct)
    return wrapper


def _get_converter(id_field: Any | None) -> Callable:
    """Returns `convert_to_dto` or `convert_to_dto_with_id`"""
    converter = convert_to_dto
    if id_field:
        converter = convert_to_dto_with_id(id_field=id_field)
    return converter
