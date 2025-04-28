import inspect
import types
import warnings
from dataclasses import is_dataclass
from functools import partial
from typing import (
    Any,
    Callable,
    NoReturn,
    get_args,
    get_origin,
    get_type_hints,
)

import pymongo
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import (
    DTO,
    Access,
    CollectionProvider,
    Dataclass,
    Index,
    MetaAttributes,
)


def raise_exc(exc: Exception | type[Exception]) -> NoReturn:
    """Allows to write one-lined exceptions."""
    raise exc


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


def _get_meta(cls) -> type:
    """Tries to get `Meta` class for the class or raises `NoMetaException`
    exception."""
    meta = cls.__dict__.get('Meta', None)
    if not meta:
        raise exceptions.NoMetaException
    if not isinstance(meta, type):
        raise exceptions.NoMetaException
    return meta


def _get_meta_attributes(cls: type) -> MetaAttributes:
    """Collect all available attributes from `Meta` class."""
    meta = _get_meta(cls)

    dto_type: type[Dataclass] | None = getattr(meta, 'dto', None)

    collection: AsyncIOMotorCollection | Collection[Any] | None = getattr(meta, 'collection', None)

    index: Index | str | None = getattr(meta, 'index', None)

    method_access: Access | None = getattr(meta, 'method_access', None)

    substitute: dict[str, str] | None = getattr(meta, 'substitute', None)
    if substitute is not None:
        warnings.warn("'substitute' dictionary is deprecated, please pass arguments in other place")

    id_field: str | None = getattr(meta, 'id_field', None)

    return MetaAttributes(
        dto=dto_type,
        collection=collection,  # type: ignore
        index=index,
        method_access=method_access,
        substitute=substitute,
        id_field=id_field,
    )


def get_first_arg(type_hint) -> Any:
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


def _create_index(index: Index | str, collection: Collection) -> None:
    """### Creates an index for the collection

    * index parameter can be string or `mongorepo.Index`
    * If index is string, creates standard mongodb index
    * If it's `mongorepo.Index` creates index with user's settings

    """
    if isinstance(index, str):
        collection.create_index(index)
        return
    index_name = index.name or f'index_{index.field}'
    direction = pymongo.DESCENDING if index.desc else pymongo.ASCENDING
    collection.create_index(
        [(index.field, direction)],
        name=index_name,
        unique=index.unique,
    )


async def _create_index_async(index: Index | str, collection: AsyncIOMotorCollection) -> None:
    """### Creates an index for the collection

    * index parameter can be string or mongorepo.Index
    * If index is string, create standard mongodb index
    * If it's `mongorepo.Index` creates index with user's settings

    """
    if isinstance(index, str):
        await collection.create_index(index)
        return
    index_name = f'index_{index.field}'
    if index.name:
        index_name = index.name
    direction = pymongo.DESCENDING if index.desc else pymongo.ASCENDING
    await collection.create_index(
        [(index.field, direction)],
        name=index_name,
        unique=index.unique,
    )


def _get_dto_from_origin(cls: type) -> type[Dataclass]:
    """
    Tries to get `dto` from origin of the class or raises an exception

    ```
    class A[UserDTO]: ...

    _get_dto_from_origin(A)  # UserDTO

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
        raise exceptions.NoDTOTypeException

    return dto


def _convert_to_dto(dto_type: type[DTO], dct: dict[str, Any]) -> DTO:
    """Converts document to dto, does not include mongodb `_id`"""
    dct.pop('_id') if dct.get('_id', None) else ...
    return dto_type(**dct)


def _convert_to_dto_with_id(
    id_field: str,
) -> Callable:
    """Converts document to dto, includes mongodb `_id` allows to set specific
    field where to store `_id`"""
    def wrapper(dto_type: type[DTO], dct: dict[str, Any]) -> DTO:
        dct[id_field] = str(dct.pop('_id'))
        return dto_type(**dct)
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


def _get_converter(
    dto_type: type[DTO], id_field: str | None = None,
) -> Callable[[type[DTO], dict[str, Any]], DTO]:
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

    converter: Callable[[type[DTO], dict[str, Any]], DTO] | partial = _convert_to_dto
    r = _has_dataclass_fields(dto_type=dto_type)
    if r:
        converter = partial(_nested_convert_to_dto, id_field=id_field)
    elif id_field is not None:
        converter = _convert_to_dto_with_id(id_field=id_field)
    return converter


def _has_dataclass_fields(dto_type: type[DTO]) -> bool:
    type_hints = get_dataclass_type_hints(dto_type)
    for v in type_hints.values():
        if is_dataclass(v):
            return True
    return False


def _check_valid_field_type(field_name: str, dto_type: type[DTO], data_type: type) -> None:
    field = dto_type.__annotations__.get(field_name, None)
    if field is None:
        raise exceptions.MongorepoException(
            message=f'{dto_type} does not have field "{field_name}"',
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


def _get_defaults(func: Callable) -> dict[str, Any]:
    """Return default values for function parameters if any provided."""
    result = {}
    params = inspect.signature(func).parameters
    for param in params.values():
        if param.default is not inspect._empty:
            result[param.name] = param.default
    return result


def use_collection[T](
    collection: AsyncIOMotorCollection | Collection[Any],
) -> Callable[[T], T]:
    """Decorator to bind a specific MongoDB collection to a repository class.

    This is useful when dynamically selecting a collection for repositories
    that are decorated with `mongorepo.repository`, `mongorepo.async_repository`,
    or `mongorepo.implement.implement`. It also works with repositories that
    inherit from `mongorepo.BaseMongoRepository` or `mongorepo.BaseAsyncMongoRepository`.

    ### Features:
    - Works with any class decorated using:
      - :class:`mongorepo.repository`
      - :class:`mongorepo.async_repository`
      - :class:`mongorepo.implement.implement`
    - Supports classes that inherit from:
      - :class:`mongorepo.BaseMongoRepository`
      - :class:`mongorepo.BaseAsyncMongoRepository`
    - Enables dynamic lookup of collections at runtime.

    ### Example:
    ```python
    from mongorepo import repository
    from my_project.database import my_collection

    # 1. Using the decorator on a repository class
    @use_collection(my_collection)
    @repository(add=True, get=True)
    class Repository:
        class Meta:
            dto = SimpleDTO

    # 2. Applying the decorator dynamically
    def provide_repository() -> Repository:
        return use_collection(my_collection)(Repository)()

    repo = provide_repository()
    ```

    """
    def wrapper(cls: T) -> T:
        provider = CollectionProvider(cls, collection)  # type: ignore
        if (__mongorepo__ := getattr(cls, '__mongorepo__', None)) is not None:
            __mongorepo__['collection_provider'] = provider  # type: ignore
        else:
            setattr(cls, '__mongorepo__', {'collection_provider': provider, 'methods': {}})
        return cls
    return wrapper


def set_meta_attrs[T](
    index: Index | str | None = None,
    dto_type: type[Dataclass] | None = None,
    method_access: Access | None = None,
    id_field: str | None = None,
    collection: AsyncIOMotorCollection | Collection | None = None,
) -> Callable[[T], T]:
    """
    Decorator that simulate work of `Meta` class inside of any mongorepo repository
    Usage example::

        # 1.
        @mongorepo.repository
        @mongorepo.use_collection(coll)
        @set_meta_attrs(dto_type=SimpleDTO)
        class FirstRepository:
            ...

        # 2.
        @implement(AddMethod(IRepo.add, dto='simple'), GetMethod(IRepo.get, filters=['x']))
        @mongorepo.set_meta_attrs(dto_type=SimpleDTO, collection=coll)
        class SecondRepository:
            ...

        # 3.
        @mongorepo.set_meta_attrs(
            id_field='x', index='x', dto_type=ComplicatedDTO, collection=coll,
        )
        class ThirdRepository(mongorepo.BaseMongoRepository):
            ...

    """
    if (
        index is None
        and dto_type is None
        and method_access is None
        and id_field is None
    ):
        raise ValueError('Provide at least one of the parameters')

    def wrapper(cls: T) -> T:
        try:
            meta = _get_meta(cls)
        except exceptions.NoMetaException:
            meta = type('Meta', (), {})
            setattr(cls, 'Meta', meta)

        if index is not None:
            setattr(meta, 'index', index)

        if dto_type is not None:
            setattr(meta, 'dto', dto_type)

        if id_field is not None:
            setattr(meta, 'id_field', id_field)

        if method_access is not None:
            setattr(meta, 'method_access', method_access)

        if collection is not None:
            setattr(meta, 'collection', collection)

        return cls

    return wrapper
