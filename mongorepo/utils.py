import inspect
from dataclasses import is_dataclass
from types import UnionType
from typing import Any, Callable, NoReturn, Optional, Type, TypeVar, get_args, get_origin

import pymongo
from pymongo.collection import Collection

from mongorepo import DTO, Access, Index
from mongorepo import exceptions


def _get_collection_and_dto(cls: type, raise_exceptions: bool = True) -> dict[str, Any]:
    """Collect `dto` and `collection` attributes from `Meta` class"""
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
    * use `mongorepo.docs.get_available_meta_attributes` to get all available `Meta` attributes
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


def _get_validated_type_hint(hint: Any, get_type: bool = False) -> Any:
    args = get_args(hint)
    if len(args) > 2:
        raise exceptions.TypeHintException(message=f'Too many arguments for type hint: {hint}')
    if len(args) == 2 and get_origin(hint) is not dict:
        if type(None) not in args:
            raise exceptions.TypeHintException(message=f'"|" allowed only with NoneType {hint}')
    for arg in args:
        if get_origin(arg) is list:
            raise exceptions.TypeHintException(
                message=f'Sequence must be the only one type hint {hint}:{arg}'
            )
        if type(arg) is UnionType or type(hint) is Optional:
            raise exceptions.TypeHintException(message=f'Invalid type hint {hint}:{arg}')
        elif is_dataclass(hint):
            get_dto_type_hints(hint)
    if get_type:
        if get_origin(hint) is list:
            return get_origin(hint)
        if args:
            for arg in args:
                if type(arg) is not None:
                    return get_origin(arg)
    return hint


def get_dto_type_hints(dto: Type[DTO] | DTO, get_types: bool = True) -> dict[str, Any]:
    """Returns dictionary of fields' type hints for a dataclass or dataclass instance"""
    default_values = {}
    for field_name, value in dto.__annotations__.items():
        hint = _get_validated_type_hint(value, get_type=get_types)
        default_values[field_name] = hint if get_types else value
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

    Tries to get `dto` from origin of the class or raises an exception

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


def convert_to_dto(dto_type: Type[DTO], dct: dict[str, Any]) -> DTO:
    """
    Converts document to dto, does not include mongodb `_id`
    """
    dct.pop('_id')
    return dto_type(**dct)


def convert_to_dto_with_id(
    id_field: str,
) -> Callable:
    """
    Converts document to dto,
    icludes mongodb `_id` allows to set specific field where to store `_id`
    """
    def wrapper(dto_type: Type[DTO], dct: dict[str, Any]) -> DTO:
        dct[id_field] = str(dct.pop('_id'))
        return dto_type(**dct)
    return wrapper


def recursive_convert_to_dto(dto_type: Type[DTO], id_field: str | None = None) -> Callable:
    def decorator(dto_type: Type[DTO], dct: dict[str, Any]) -> DTO:
        def wrapper(
            dto_type: Type[DTO], dct: dict[str, Any], to_dto: bool = False,
        ) -> dict[str, Any] | DTO:
            type_hints = get_dto_type_hints(dto_type, get_types=False)
            data = {}
            for key, value in dct.items():
                if is_dataclass(type_hints.get(key, None)):
                    data[key] = wrapper(type_hints.get(key, None), value, to_dto=True)
                elif get_origin(type_hints.get(key, None)) is list and isinstance(value, list):
                    args = get_args(type_hints.get(key, None))
                    if is_dataclass(args[0]):
                        data[key] = [
                            wrapper(args[0], v, to_dto=True) for v in value  # type: ignore
                        ]
                    else:
                        data[key] = value
                else:
                    data[key] = value
            return dto_type(**data) if to_dto else data
        data = {}
        if id_field is not None:
            data[id_field] = str(dct.pop('_id'))
        else:
            dct.pop('_id') if dct.get('_id', None) else ...
        data.update(wrapper(dto_type, dct))  # type: ignore
        return dto_type(**data)
    return decorator


def _get_converter(dto_type: Type[DTO], id_field: str | None = None) -> Callable:
    """
    Returns proper converter based on type hints of the dto
    """
    converter = convert_to_dto
    r = _has_dataclass_fields(dto_type=dto_type)
    if r:
        converter = recursive_convert_to_dto(dto_type, id_field)
    elif id_field is not None:
        converter = convert_to_dto_with_id(id_field=id_field)
    return converter


def _has_dataclass_fields(dto_type: Type[DTO]) -> bool:
    type_hints = get_dto_type_hints(dto_type, get_types=False)
    for value in type_hints.values():
        if is_dataclass(value):
            return True
        elif get_origin(value) is list:
            args = get_args(value)
            if is_dataclass(args[0]):
                return True
    return False


def raise_exc(exc: Exception) -> NoReturn:
    """Allows to write one-lined exceptions"""
    raise exc


def _validate_method_annotations(method: Callable) -> None:
    if not method.__annotations__:
        raise exceptions.MongoRepoException(message=f'No type hints for {method.__name__}()')
    if 'return' not in method.__annotations__:
        raise exceptions.MongoRepoException(
            message=f'return type is not specified for "{method}" method',
        )
    params = inspect.signature(method).parameters
    if list(params)[0] != 'self':
        raise exceptions.MongoRepoException(
            message=f'First parameter must be self: "{method}" method',
        )
    for param, type_hint in params.items():
        if param == 'self':
            continue
        if type_hint == inspect._empty and type_hint.kind not in [
            inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL
        ]:
            raise exceptions.MongoRepoException(
                message=f'Parameter "{param}" does not have type hint',
            )


def replace_typevars(func: Callable, typevar: Any) -> None:
    for param, anno in func.__annotations__.items():
        if isinstance(anno, TypeVar):
            func.__annotations__[param] = typevar
