import asyncio
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generator, Generic

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo._base import DTO, Dataclass, Index, MetaAttributes
from mongorepo._collections import COLLECTION_PROVIDER, CollectionProvider
from mongorepo._methods.impl import (
    AddBatchMethod,
    AddMethod,
    DeleteMethod,
    GetAllMethod,
    GetListMethod,
    GetMethod,
    UpdateMethod,
)
from mongorepo._methods.impl_async import (
    AddBatchMethodAsync,
    AddMethodAsync,
    DeleteMethodAsync,
    GetAllMethodAsync,
    GetListMethodAsync,
    GetMethodAsync,
    UpdateMethodAsync,
)
from mongorepo.utils import (
    _create_index,
    _create_index_async,
    _get_converter,
    _get_dto_from_origin,
    _get_meta_attributes,
)

if TYPE_CHECKING:
    from pymongo.results import InsertManyResult


class BaseMongoRepository(Generic[DTO]):
    """
    ## Base MongoDB repository class
    #### Extends child classes with various methods:

    ```
    add(self, dto: DTO) -> DTO
    get(self, **filters) -> DTO | None
    get_all(self, **filters) -> Iterable[DTO]
    update(self, dto: DTO, **filters) -> DTO
    delete(self, **filters) -> bool
    ```

    #### Provide DTO type in type hints, example:

    ```
    class DummyMongoRepository(BaseMongoRepository[UserDTO]):
        ...
    ```

    * If you want to create an index use `mongorepo.Index`
      or just a name of the field to put index on
    """

    def __new__(cls, *args, **kwargs) -> 'BaseMongoRepository[DTO]':
        instance = super().__new__(cls)
        dto_type = _get_dto_from_origin(cls)

        try:
            meta: MetaAttributes[Collection] | None = _get_meta_attributes(cls)
        except exceptions.NoMetaException:
            meta = None

        id_field: str | None = meta['id_field'] if meta else None
        collection: Collection | None = meta['collection'] if meta else None
        index: Index | str | None = meta['index'] if meta else None

        if not hasattr(cls, COLLECTION_PROVIDER):
            setattr(cls, COLLECTION_PROVIDER, CollectionProvider(collection))

        if index is not None:
            if collection is None:
                raise exceptions.NoCollectionException(
                    message='Index can be created only if collection provided in Meta class',
                )
            _create_index(index, collection=collection)
        converter = _get_converter(dto_type, id_field)
        setattr(
            instance,
            '_mongorepo_add',
            AddMethod(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )
        setattr(
            instance,
            '_mongorepo_add_batch',
            AddBatchMethod(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )
        setattr(
            instance,
            '_mongorepo_get',
            GetMethod(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )
        setattr(
            instance,
            '_mongorepo_get_list',
            GetListMethod(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )
        setattr(
            instance,
            '_mongorepo_get_all',
            GetAllMethod(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )
        setattr(
            instance,
            '_mongorepo_update',
            UpdateMethod(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )
        setattr(
            instance,
            '_mongorepo_delete',
            DeleteMethod(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )

        return instance

    def get(self, **filters: Any) -> DTO | None:
        return self._mongorepo_get(**filters)  # type: ignore

    def get_all(self, **filters: Any) -> Generator[DTO, None, None]:
        yield from self._mongorepo_get_all(**filters)  # type: ignore

    def get_list(self, offset: int = 0, limit: int = 20, **filters: Any) -> list[DTO]:
        return self._mongorepo_get_list(offset=offset, limit=limit, **filters)  # type: ignore

    def add(self, dto: DTO) -> DTO:
        return self._mongorepo_add(dto)  # type: ignore

    def add_batch(self, dto_list: list[DTO]) -> 'InsertManyResult':
        return self._mongorepo_add_batch(dto_list)  # type: ignore

    def update(self, dto: Dataclass, **filters: Any) -> DTO | None:
        return self._mongorepo_update(dto, **filters)  # type: ignore

    def delete(self, **filters: Any) -> bool:
        return self._mongorepo_delete(**filters)  # type: ignore


class BaseAsyncMongoRepository(Generic[DTO]):
    """
    ## Base MongoDB repository class
    #### Extends child classes with various methods:

    ```
    add(self, dto: DTO) -> DTO
    get(self, **filters) -> DTO | None
    get_all(self, **filters) -> Iterable[DTO]
    update(self, dto: DTO, **filters) -> DTO
    delete(self, **filters) -> bool
    ```

    #### Provide DTO type in type hints, example:

    ```
    class DummyMongoRepository(BaseMongoRepository[UserDTO]):
        ...
    ```

    * If you want to create an index use `mongorepo.Index`
      or just a name of the field to put index on
    """

    def __new__(cls, *args, **kwargs) -> 'BaseAsyncMongoRepository[DTO]':
        instance = super().__new__(cls)
        dto_type = _get_dto_from_origin(cls)

        try:
            meta: MetaAttributes[AsyncIOMotorCollection] | None = _get_meta_attributes(cls)
        except exceptions.NoMetaException:
            meta = None

        id_field: str | None = meta['id_field'] if meta else None
        collection: AsyncIOMotorCollection | None = meta['collection'] if meta else None
        index: Index | str | None = meta['index'] if meta else None

        if not hasattr(cls, COLLECTION_PROVIDER):
            setattr(cls, COLLECTION_PROVIDER, CollectionProvider(collection))

        if index is not None:
            if collection is None:
                raise exceptions.NoCollectionException(
                    message='Index can be created only if collection provided in Meta class',
                )
            asyncio.create_task(_create_index_async(index, collection=collection))
        converter = _get_converter(dto_type, id_field)
        setattr(
            instance,
            '_mongorepo_add',
            AddMethodAsync(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )
        setattr(
            instance,
            '_mongorepo_add_batch',
            AddBatchMethodAsync(
                dto_type, cls, id_field=id_field, converter=converter,  # type: ignore
            ),
        )
        setattr(
            instance,
            '_mongorepo_get',
            GetMethodAsync(dto_type, cls, id_field=id_field, converter=converter),  # type: ignore
        )
        setattr(
            instance,
            '_mongorepo_get_list',
            GetListMethodAsync(
                dto_type, cls, id_field=id_field, converter=converter,  # type: ignore
            ),
        )
        setattr(
            instance,
            '_mongorepo_get_all',
            GetAllMethodAsync(
                dto_type, cls, id_field=id_field, converter=converter,  # type: ignore
            ),
        )
        setattr(
            instance,
            '_mongorepo_update',
            UpdateMethodAsync(
                dto_type, cls, id_field=id_field, converter=converter,  # type: ignore
            ),
        )
        setattr(
            instance,
            '_mongorepo_delete',
            DeleteMethodAsync(
                dto_type, cls, id_field=id_field, converter=converter,  # type: ignore
            ),
        )

        return instance

    async def get(self, **filters: Any) -> DTO | None:
        return await self._mongorepo_get(**filters)  # type: ignore

    def get_all(self, **filters: Any) -> AsyncGenerator[DTO, None]:
        return self._mongorepo_get_all(**filters)  # type: ignore

    async def get_list(self, offset: int = 0, limit: int = 20, **filters: Any) -> list[DTO]:
        return await self._mongorepo_get_list(offset=offset, limit=limit, **filters)  # type: ignore

    async def add(self, dto: DTO) -> DTO:
        return await self._mongorepo_add(dto)  # type: ignore

    async def add_batch(self, dto_list: list[DTO]) -> 'InsertManyResult':
        return await self._mongorepo_add_batch(dto_list)  # type: ignore

    async def update(self, dto: Dataclass, **filters: Any) -> DTO | None:
        return await self._mongorepo_update(dto, **filters)  # type: ignore

    async def delete(self, **filters: Any) -> bool:
        return await self._mongorepo_delete(**filters)  # type: ignore
