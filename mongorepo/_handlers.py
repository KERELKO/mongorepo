from dataclasses import asdict
from typing import Any, Iterable

from motor.motor_asyncio import (
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
)
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

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
from mongorepo.types import (
    CollectionProvider,
    Field,
    MongorepoDict,
    RepositoryConfig,
    get_method_access_prefix,
)
from mongorepo.utils.dataclass_converters import get_converter
from mongorepo.utils.field_factory import build_validated_field
from mongorepo.utils.mongorepo_dict import get_or_create_mongorepo_dict
from mongorepo.utils.type_hints import (
    check_valid_field_type,
    get_entity_type_hints,
)
from mongorepo.utils.validations import validate_repository_config_converters


def _handle_mongo_repository(
    cls,
    config: RepositoryConfig,
    add: bool,
    get: bool,
    add_batch: bool,
    get_all: bool,
    update: bool,
    delete: bool,
    get_list: bool,
    list_fields: Iterable[str] | None,
    integer_fields: Iterable[str] | None,
) -> type:
    validate_repository_config_converters(config)
    prefix = get_method_access_prefix(
        access=config.method_access if not config.method_access else config.method_access, cls=cls,
    )

    config.to_document_converter = config.to_document_converter or asdict
    config.to_entity_converter = config.to_entity_converter or get_converter(config.entity_type)
    entity_type_hints = get_entity_type_hints(config.entity_type)

    __mongorepo__: MongorepoDict[ClientSession, Collection[Any]] = get_or_create_mongorepo_dict(
        cls,
        CollectionProvider(obj=cls, collection=config.collection),
        config,
    )

    if add:
        key = f'{prefix}add'
        add_method = AddMethod(
            config.entity_type, owner=cls, to_document_converter=config.to_document_converter,
        )
        __mongorepo__['methods'][key] = add_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if add_batch:
        key = f'{prefix}add_batch'
        add_batch_method = AddBatchMethod(
            config.entity_type, cls, to_document_converter=config.to_document_converter,
        )
        __mongorepo__['methods'][key] = add_batch_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get:
        key = f'{prefix}get'
        get_method = GetMethod(
            config.entity_type, owner=cls, to_entity_converter=config.to_entity_converter,
        )
        __mongorepo__['methods'][key] = get_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get_all:
        key = f'{prefix}get_all'
        get_all_method = GetAllMethod(
            config.entity_type, cls, to_entity_converter=config.to_entity_converter,
        )
        __mongorepo__['methods'][key] = get_all_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get_list:
        key = f'{prefix}get_list'
        get_list_method = GetListMethod(
            config.entity_type, cls, to_entity_converter=config.to_entity_converter,
        )
        __mongorepo__['methods'][key] = get_list_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if delete:
        key = f'{prefix}delete'
        delete_method: DeleteMethod = DeleteMethod(config.entity_type, cls)
        __mongorepo__['methods'][key] = delete_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if update:
        key = f'{prefix}update'
        update_method = UpdateMethod(
            config.entity_type,
            cls,
            to_entity_converter=config.to_entity_converter,
            to_document_converter=config.to_document_converter,
        )
        __mongorepo__['methods'][key] = update_method
        setattr(cls, key, __mongorepo__['methods'][key])

    if list_fields:
        for field in list_fields:
            check_valid_field_type(field, config.entity_type, list)
            target_field: Field = Field(name=field)
            build_validated_field(target_field, entity_type_hints[target_field.name], config)

            append_method: AppendListMethod = AppendListMethod(
                config.entity_type, owner=cls, target_field=target_field,
            )
            __mongorepo__['methods'][k := f'{prefix}{field}__append'] = append_method
            setattr(cls, k, __mongorepo__['methods'][k])

            remove_method: RemoveListMethod = RemoveListMethod(
                config.entity_type, owner=cls, target_field=target_field,
            )
            __mongorepo__['methods'][k := f'{prefix}{field}__remove'] = remove_method
            setattr(cls, k, __mongorepo__['methods'][k])

            pop_method: PopListMethod = PopListMethod(
                config.entity_type, owner=cls, target_field=target_field,
            )
            __mongorepo__['methods'][k := f'{prefix}{field}__pop'] = pop_method
            setattr(cls, k, __mongorepo__['methods'][k])

            list_values_method: GetListValuesMethod = GetListValuesMethod(
                config.entity_type, owner=cls, target_field=target_field,
            )
            __mongorepo__['methods'][k := f'{prefix}{field}__list'] = list_values_method
            setattr(cls, k, __mongorepo__['methods'][k])

    if integer_fields:
        for field in integer_fields:
            check_valid_field_type(field, config.entity_type, int)

            target_field = Field(name=field)
            build_validated_field(target_field, entity_type_hints[target_field.name], config)

            increment_method: IncrementIntegerFieldMethod = IncrementIntegerFieldMethod(
                config.entity_type, cls, target_field=target_field, weight=1,
            )
            __mongorepo__['methods'][k := f'{prefix}incr__{field}'] = increment_method
            setattr(cls, k, __mongorepo__['methods'][k])

            decrement_method: IncrementIntegerFieldMethod = IncrementIntegerFieldMethod(
                config.entity_type, cls, target_field=target_field, weight=-1,
            )
            __mongorepo__['methods'][k := f'{prefix}decr__{field}'] = decrement_method
            setattr(cls, k, __mongorepo__['methods'][k])

    cls.__mongorepo__ = __mongorepo__

    return cls


def _handle_async_mongo_repository(
    cls,
    config: RepositoryConfig,
    add: bool,
    add_batch: bool,
    get: bool,
    get_all: bool,
    get_list: bool,
    update: bool,
    delete: bool,
    integer_fields: Iterable[str] | None,
    list_fields: Iterable[str] | None,
) -> type:
    """Calls for functions that set different async methods and attributes to
    the class."""
    validate_repository_config_converters(config)

    prefix = get_method_access_prefix(
        access=config.method_access if not config.method_access else config.method_access, cls=cls,
    )

    config.to_document_converter = config.to_document_converter or asdict
    config.to_entity_converter = config.to_entity_converter or get_converter(config.entity_type)
    entity_type_hints = get_entity_type_hints(config.entity_type)

    __mongorepo__: MongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection] = get_or_create_mongorepo_dict(  # noqa
        cls,
        CollectionProvider(obj=cls, collection=config.collection),
        config,
    )

    if add:
        key = f'{prefix}add'
        add_method = AddMethodAsync(
            config.entity_type,
            owner=cls,
            to_document_converter=config.to_document_converter,
        )
        __mongorepo__['methods'][key] = add_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get:
        key = f'{prefix}get'
        get_method = GetMethodAsync(
            config.entity_type,
            owner=cls,
            to_entity_converter=config.to_entity_converter,
        )
        __mongorepo__['methods'][key] = get_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if add_batch:
        key = f'{prefix}add_batch'
        add_batch_method = AddBatchMethodAsync(
            config.entity_type,
            cls, to_document_converter=config.to_document_converter,
        )
        __mongorepo__['methods'][key] = add_batch_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get_all:
        key = f'{prefix}get_all'
        get_all_method = GetAllMethodAsync(config.entity_type, cls, config.to_entity_converter)
        __mongorepo__['methods'][key] = get_all_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if get_list:
        key = f'{prefix}get_list'
        get_list_method = GetListMethodAsync(config.entity_type, cls, config.to_entity_converter)
        __mongorepo__['methods'][key] = get_list_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if delete:
        key = f'{prefix}delete'
        delete_method: DeleteMethodAsync = DeleteMethodAsync(config.entity_type, cls)
        __mongorepo__['methods'][key] = delete_method
        setattr(cls, key, __mongorepo__['methods'][key])
    if update:
        key = f'{prefix}update'
        update_method = UpdateMethodAsync(
            config.entity_type,
            cls,
            to_entity_converter=config.to_entity_converter,
            to_document_converter=config.to_document_converter,
        )
        __mongorepo__['methods'][key] = update_method
        setattr(cls, key, __mongorepo__['methods'][key])

    if list_fields:
        for field in list_fields:
            check_valid_field_type(field, config.entity_type, list)

            target_field: Field = Field(name=field)
            build_validated_field(target_field, entity_type_hints[target_field.name], config)

            append_method: AppendListMethodAsync = AppendListMethodAsync(
                config.entity_type, owner=cls, target_field=target_field,
            )
            __mongorepo__['methods'][k := f'{prefix}{field}__append'] = append_method
            setattr(cls, k, __mongorepo__['methods'][k])

            remove_method: RemoveListMethodAsync = RemoveListMethodAsync(
                config.entity_type, owner=cls, target_field=target_field,
            )
            __mongorepo__['methods'][k := f'{prefix}{field}__remove'] = remove_method
            setattr(cls, k, __mongorepo__['methods'][k])

            pop_method: PopListMethodAsync = PopListMethodAsync(
                config.entity_type, owner=cls, target_field=target_field,
            )
            __mongorepo__['methods'][k := f'{prefix}{field}__pop'] = pop_method
            setattr(cls, k, __mongorepo__['methods'][k])

            list_values_method: GetListValuesMethodAsync = GetListValuesMethodAsync(
                config.entity_type, owner=cls, target_field=target_field,
            )
            __mongorepo__['methods'][k := f'{prefix}{field}__list'] = list_values_method
            setattr(cls, k, __mongorepo__['methods'][k])

    if integer_fields:
        for field in integer_fields:
            check_valid_field_type(field, config.entity_type, int)

            target_field = Field(name=field)
            build_validated_field(target_field, entity_type_hints[target_field.name], config)

            increment_method: IncrementIntegerFieldMethodAsync = IncrementIntegerFieldMethodAsync(
                config.entity_type, cls, target_field=target_field, weight=1,
            )
            __mongorepo__['methods'][k := f'{prefix}incr__{field}'] = increment_method
            setattr(cls, k, __mongorepo__['methods'][k])

            decrement_method: IncrementIntegerFieldMethodAsync = IncrementIntegerFieldMethodAsync(
                config.entity_type, cls, target_field=target_field, weight=-1,
            )
            __mongorepo__['methods'][k := f'{prefix}decr__{field}'] = decrement_method
            setattr(cls, k, __mongorepo__['methods'][k])

    cls.__mongorepo__ = __mongorepo__

    return cls
