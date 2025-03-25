import asyncio
from typing import Iterable

from motor.motor_asyncio import (
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
)
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import Access, CollectionProvider
from mongorepo._common import MongorepoDict
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
from mongorepo._methods.impl_async import (
    AddBatchMethodAsync,
    AddMethodAsync,
    AppendListMethodAsync,
    DeleteMethodAsync,
    GetAllMethodAsync,
    GetListMethodAsync,
    GetListValuesMethodAsync,
    GetMethodAsync,
    IncrementIntegerFieldMethodAsync,
    PopListMethodAsync,
    RemoveListMethodAsync,
    UpdateMethodAsync,
)
from mongorepo.utils import (
    _check_valid_field_type,
    _create_index,
    _create_index_async,
    _get_converter,
    _get_meta_attributes,
    get_prefix,
    raise_exc,
)


def _handle_mongo_repository(
    cls,
    add: bool,
    get: bool,
    add_batch: bool,
    get_all: bool,
    update: bool,
    delete: bool,
    get_list: bool,
    list_fields: Iterable[str] | None,
    integer_fields: Iterable[str] | None,
    method_access: Access | None,
) -> type:
    attributes = _get_meta_attributes(cls)

    collection = attributes['collection']
    if collection is not None and not isinstance(collection, Collection):
        raise exceptions.MongorepoException(
            f'Invalid collection type "{type(collection)}", expected: {Collection}',
        )
    dto = attributes['dto'] or raise_exc(exceptions.NoDTOTypeException)
    index = attributes['index']
    id_field = attributes['id_field']

    prefix = get_prefix(
        access=attributes['method_access'] if not method_access else method_access, cls=cls,
    )

    if index is not None and collection is not None:
        _create_index(index, collection)

    converter = _get_converter(dto, id_field)

    if hasattr(cls, '__mongorepo__'):
        __mongorepo__: MongorepoDict[ClientSession, Collection] = getattr(cls, '__mongorepo__')
    else:
        __mongorepo__ = MongorepoDict[ClientSession, Collection](
            collection_provider=CollectionProvider(obj=cls, collection=collection), methods={},
        )

    if add:
        key = f'{prefix}add'
        add_method = AddMethod(dto, owner=cls, id_field=id_field, converter=converter)
        __mongorepo__['methods'][key] = add_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if add_batch:
        key = f'{prefix}add_batch'
        add_batch_method = AddBatchMethod(dto, cls, id_field=id_field, converter=converter)
        __mongorepo__['methods'][key] = add_batch_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get:
        key = f'{prefix}get'
        get_method = GetMethod(dto, owner=cls, id_field=id_field, converter=converter)
        __mongorepo__['methods'][key] = get_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get_all:
        key = f'{prefix}get_all'
        get_all_method = GetAllMethod(dto, cls, converter=converter)
        __mongorepo__['methods'][key] = get_all_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get_list:
        key = f'{prefix}get_list'
        get_list_method = GetListMethod(dto, cls, converter=converter)
        __mongorepo__['methods'][key] = get_list_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if delete:
        key = f'{prefix}delete'
        delete_method = DeleteMethod(dto, cls)
        __mongorepo__['methods'][key] = delete_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if update:
        key = f'{prefix}update'
        update_method = UpdateMethod(dto, cls, converter=converter)
        __mongorepo__['methods'][key] = update_method
        setattr(cls, key, __mongorepo__['methods'][key])

    if list_fields:
        for field in list_fields:
            _check_valid_field_type(field, dto, list)

            append_method = AppendListMethod(dto_type=dto, owner=cls, field_name=field)
            __mongorepo__['methods'][k := f'{prefix}{field}__append'] = append_method
            setattr(cls, k, __mongorepo__['methods'][k])

            remove_method = RemoveListMethod(dto_type=dto, owner=cls, field_name=field)
            __mongorepo__['methods'][k := f'{prefix}{field}__remove'] = remove_method
            setattr(cls, k, __mongorepo__['methods'][k])

            pop_method = PopListMethod(dto_type=dto, owner=cls, field_name=field)
            __mongorepo__['methods'][k := f'{prefix}{field}__pop'] = pop_method
            setattr(cls, k, __mongorepo__['methods'][k])

            list_values_method = GetListValuesMethod(dto_type=dto, owner=cls, field_name=field)
            __mongorepo__['methods'][k := f'{prefix}{field}__list'] = list_values_method
            setattr(cls, k, __mongorepo__['methods'][k])

    if integer_fields:
        for field in integer_fields:
            _check_valid_field_type(field, dto, int)

            increment_method = IncrementIntegerFieldMethod(
                dto, cls, field_name=field, weight=1,
            )
            __mongorepo__['methods'][k := f'{prefix}incr__{field}'] = increment_method
            setattr(cls, k, __mongorepo__['methods'][k])

            decrement_method = IncrementIntegerFieldMethod(
                dto, cls, field_name=field, weight=-1,
            )
            __mongorepo__['methods'][k := f'{prefix}decr__{field}'] = decrement_method
            setattr(cls, k, __mongorepo__['methods'][k])

    cls.__mongorepo__ = __mongorepo__

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
    integer_fields: Iterable[str] | None,
    list_fields: Iterable[str] | None,
    method_access: Access | None,
) -> type:
    """Calls for functions that set different async methods and attributes to
    the class."""
    attributes = _get_meta_attributes(cls)

    collection = attributes['collection']
    if collection is not None and not isinstance(collection, AsyncIOMotorCollection):
        raise exceptions.MongorepoException(
            f'Invalid collection type "{type(collection)}", expected: {AsyncIOMotorCollection}',
        )
    dto = attributes['dto'] or raise_exc(exceptions.NoDTOTypeException)
    index = attributes['index']
    id_field = attributes['id_field']

    prefix = get_prefix(
        access=attributes['method_access'] if not method_access else method_access, cls=cls,
    )

    if hasattr(cls, '__mongorepo__'):
        __mongorepo__: MongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection] = getattr(cls, '__mongorepo__')  # noqa
    else:
        __mongorepo__ = MongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection](
            collection_provider=CollectionProvider(obj=cls, collection=collection), methods={},
        )

    if index is not None and collection is not None:
        asyncio.create_task(_create_index_async(index, collection))

    converter = _get_converter(dto, id_field)

    if add:
        key = f'{prefix}add'
        add_method = AddMethodAsync(dto, owner=cls, id_field=id_field, converter=converter)
        __mongorepo__['methods'][key] = add_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if add_batch:
        key = f'{prefix}add_batch'
        add_batch_method = AddBatchMethodAsync(dto, cls, id_field=id_field, converter=converter)
        __mongorepo__['methods'][key] = add_batch_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get:
        key = f'{prefix}get'
        get_method = GetMethodAsync(dto, owner=cls, id_field=id_field, converter=converter)
        __mongorepo__['methods'][key] = get_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get_all:
        key = f'{prefix}get_all'
        get_all_method = GetAllMethodAsync(dto, cls, converter=converter)
        __mongorepo__['methods'][key] = get_all_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get_list:
        key = f'{prefix}get_list'
        get_list_method = GetListMethodAsync(dto, cls, converter=converter)
        __mongorepo__['methods'][key] = get_list_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if delete:
        key = f'{prefix}delete'
        delete_method = DeleteMethodAsync(dto, cls)
        __mongorepo__['methods'][key] = delete_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if update:
        key = f'{prefix}update'
        update_method = UpdateMethodAsync(dto, cls, converter=converter)
        __mongorepo__['methods'][key] = update_method
        setattr(cls, key, __mongorepo__['methods'][key])

    if list_fields:
        for field in list_fields:
            _check_valid_field_type(field, dto, list)

            append_method = AppendListMethodAsync(dto_type=dto, owner=cls, field_name=field)
            __mongorepo__['methods'][k := f'{prefix}{field}__append'] = append_method
            setattr(cls, k, __mongorepo__['methods'][k])

            remove_method = RemoveListMethodAsync(dto_type=dto, owner=cls, field_name=field)
            __mongorepo__['methods'][k := f'{prefix}{field}__remove'] = remove_method
            setattr(cls, k, __mongorepo__['methods'][k])

            pop_method = PopListMethodAsync(dto_type=dto, owner=cls, field_name=field)
            __mongorepo__['methods'][k := f'{prefix}{field}__pop'] = pop_method
            setattr(cls, k, __mongorepo__['methods'][k])

            list_values_method = GetListValuesMethodAsync(dto_type=dto, owner=cls, field_name=field)
            __mongorepo__['methods'][k := f'{prefix}{field}__list'] = list_values_method
            setattr(cls, k, __mongorepo__['methods'][k])

    if integer_fields:
        for field in integer_fields:
            _check_valid_field_type(field, dto, int)

            increment_method = IncrementIntegerFieldMethodAsync(
                dto, cls, field_name=field, weight=1,
            )
            __mongorepo__['methods'][k := f'{prefix}incr__{field}'] = increment_method
            setattr(cls, k, __mongorepo__['methods'][k])

            decrement_method = IncrementIntegerFieldMethodAsync(
                dto, cls, field_name=field, weight=-1,
            )
            __mongorepo__['methods'][k := f'{prefix}decr__{field}'] = decrement_method
            setattr(cls, k, __mongorepo__['methods'][k])

    cls.__mongorepo__ = __mongorepo__

    return cls
