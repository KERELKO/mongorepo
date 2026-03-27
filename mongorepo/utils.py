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

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import (
    Entity,
    Access,
    CollectionProvider,
    Dataclass,
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

    entity_type: type[Dataclass] | None = getattr(meta, 'entity', None)

    collection: AsyncIOMotorCollection | Collection[Any] | None = getattr(meta, 'collection', None)

    method_access: Access | None = getattr(meta, 'method_access', None)

    substitute: dict[str, str] | None = getattr(meta, 'substitute', None)
    if substitute is not None:
        warnings.warn("'substitute' dictionary is deprecated, please pass arguments in other place")

    id_field: str | None = getattr(meta, 'id_field', None)

    return MetaAttributes(
        entity=entity_type,
        collection=collection,  # type: ignore
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


def _convert_to_dto(entity_type: type[Entity], dct: dict[str, Any]) -> Entity:
    """Converts document to entity, does not include mongodb `_id`"""
    dct.pop('_id') if dct.get('_id', None) else ...
    return entity_type(**dct)


def _convert_to_dto_with_id(
    id_field: str,
) -> Callable:
    """Converts document to entity, includes mongodb `_id` allows to set specific
    field where to store `_id`"""
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


def _get_converter(
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
    r = _has_dataclass_fields(entity_type=entity_type)
    if r:
        converter = partial(_nested_convert_to_dto, id_field=id_field)
    elif id_field is not None:
        converter = _convert_to_dto_with_id(id_field=id_field)
    return converter


def _has_dataclass_fields(entity_type: type[Entity]) -> bool:
    type_hints = get_dataclass_type_hints(entity_type)
    for v in type_hints.values():
        if is_dataclass(v):
            return True
    return False


def _check_valid_field_type(field_name: str, entity_type: type[Entity], data_type: type) -> None:
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
            entity = SimpleEntity

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
    entity_type: type[Dataclass] | None = None,
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
        @set_meta_attrs(entity_type=SimpleEntity)
        class FirstRepository:
            ...

        # 2.
        @implement(AddMethod(IRepo.add, entity='simple'), GetMethod(IRepo.get, filters=['x']))
        @mongorepo.set_meta_attrs(entity_type=SimpleEntity, collection=coll)
        class SecondRepository:
            ...

        # 3.
        @mongorepo.set_meta_attrs(
            id_field='x', entity_type=MultiFieldEntity, collection=coll,
        )
        class ThirdRepository(mongorepo.BaseMongoRepository):
            ...

    """
    if (
        entity_type is None
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

        if entity_type is not None:
            setattr(meta, 'entity', entity_type)

        if id_field is not None:
            setattr(meta, 'id_field', id_field)

        if method_access is not None:
            setattr(meta, 'method_access', method_access)

        if collection is not None:
            setattr(meta, 'collection', collection)

        return cls

    return wrapper
