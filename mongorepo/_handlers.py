from typing import Any, Iterable, cast

from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import Access
from mongorepo._methods.impl import (
    AddBatchMethod,
    AddMethod,
    AppendListMethod,
    DeleteMethod,
    GetAllMethod,
    GetListMethod,
    GetListValuesMethod,
    GetMethod,
    IncrementIntegerFieldMethod,
    PopListMethod,
    RemoveListMethod,
    UpdateMethod,
)
from mongorepo.utils import (
    _check_valid_field_type,
    _create_index,
    _get_converter,
    _get_meta_attributes,
    get_prefix,
    raise_exc,
)

from ._collections import COLLECTION_PROVIDER, CollectionProvider


def _handle_mongo_repository(
    cls,
    add: bool,
    get: bool,
    add_batch: bool,
    get_all: bool,
    update: bool,
    delete: bool,
    get_list: bool,
    __methods__: bool,
    list_fields: Iterable[str] | None,
    integer_fields: Iterable[str] | None,
    method_access: Access | None,
) -> type:
    attributes = _get_meta_attributes(cls)

    collection: Collection[Any] | None = cast(Collection, attributes['collection'])
    dto = attributes['dto'] or raise_exc(exceptions.NoDTOTypeException)
    index = attributes['index']
    id_field = attributes['id_field']

    prefix = get_prefix(
        access=attributes['method_access'] if not method_access else method_access, cls=cls,
    )

    if not hasattr(cls, COLLECTION_PROVIDER):
        setattr(cls, COLLECTION_PROVIDER, CollectionProvider(collection))

    if index is not None and collection is not None:
        _create_index(index, collection)

    converter = _get_converter(dto, id_field)

    if add:
        setattr(
            cls, f'{prefix}add', AddMethod(dto, owner=cls, id_field=id_field, converter=converter),
        )
    if add_batch:
        setattr(
            cls,
            f'{prefix}add_batch',
            AddBatchMethod(dto, owner=cls, id_field=id_field, converter=converter),
        )
    if get:
        setattr(
            cls, f'{prefix}get', GetMethod(dto, owner=cls, id_field=id_field, converter=converter),
        )
    if get_all:
        setattr(
            cls, f'{prefix}get_all', GetAllMethod(dto, cls, converter=converter),
        )
    if get_list:
        setattr(
            cls, f'{prefix}get_list', GetListMethod(dto, cls, converter=converter),
        )
    if delete:
        setattr(cls, f'{prefix}delete', DeleteMethod(dto, cls))
    if update:
        setattr(cls, f'{prefix}update', UpdateMethod(dto, cls, converter=converter))

    if list_fields:
        for field in list_fields:
            _check_valid_field_type(field, dto, list)

            append_method = AppendListMethod(dto_type=dto, owner=cls, field_name=field)
            remove_method = RemoveListMethod(dto_type=dto, owner=cls, field_name=field)
            pop_method = PopListMethod(dto_type=dto, owner=cls, field_name=field)
            list_values_method = GetListValuesMethod(dto_type=dto, owner=cls, field_name=field)

            setattr(cls, f'{prefix}{field}__append', append_method)
            setattr(cls, f'{prefix}{field}__remove', remove_method)
            setattr(cls, f'{prefix}{field}__pop', pop_method)
            setattr(cls, f'{prefix}{field}__list', list_values_method)

    if integer_fields:
        for field in integer_fields:
            _check_valid_field_type(field, dto, int)

            increment_method = IncrementIntegerFieldMethod(dto, cls, field_name=field, weight=1)
            decrement_method = IncrementIntegerFieldMethod(dto, cls, field_name=field, weight=-1)

            setattr(cls, f'{prefix}incr__{field}', increment_method)
            setattr(cls, f'{prefix}decr__{field}', decrement_method)

    return cls


def _handle_async_mongo_repository(
    cls,
    add: bool,
    add_batch: bool,
    get: bool,
    get_all: bool,
    get_list: bool,
    update: bool,
    delete: bool,
    __methods__: bool,
    integer_fields: list[str] | None,
    array_fields: list[str] | None,
    method_access: Access | None,
) -> type:
    """Calls for functions that set different async methods and attributes to
    the class."""
    return cls
