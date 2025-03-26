import asyncio
from typing import Any, AsyncGenerator, Generator, Generic

from motor.motor_asyncio import (
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
)
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.results import InsertManyResult

from mongorepo import exceptions
from mongorepo._base import DTO, Dataclass, Index, MetaAttributes
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
    CollectionProvider,
    _create_index,
    _create_index_async,
    _get_converter,
    _get_dto_from_origin,
    _get_meta_attributes,
)

from ._common import MongorepoDict


class BaseMongoRepository(Generic[DTO]):
    """## Base MongoDB Repository

    This class provides a foundation for creating synchronous repositories using MongoDB.
    It dynamically extends child classes with various CRUD operations and integrates
    with MongoDB collections.

    ### Features:
    - **Automatic method injection**: Methods like `add`, `get`, `update`, and `delete`
      are dynamically attached.
    - **Index creation**: Supports indexing using `mongorepo.Index` or a simple field name.
    - **DTO-based operations**: Ensures type safety with a provided Data Transfer Object (DTO).
    - **Meta class support**: The child class can define a `Meta` class with:
      - `dto`: A dataclass representing the document structure.
      - `collection`: An instance of `Collection` representing the MongoDB collection.
      - `index` (optional): Defines an index for efficient querying.

    ### Required:
    - **Collection**: Provide a collection of type `Collection` either in the `Meta` class or
      with the `mongorepo.use_collection` decorator.
    - **DTO**: Provide the DTO type in Generic
      (e.g. `class Repo(BaseMongoRepository[MyDataclass])`) or in the `Meta` class.

    ### Available Methods:
    - `add(self, dto: DTO) -> DTO`
    - `add_batch(self, dto_list: list[DTO]) -> InsertManyResult`
    - `get(self, **filters) -> DTO | None`
    - `get_all(self, **filters) -> Iterable[DTO]`
    - `get_list(self, offset: int = 0, limit: int = 20, **filters) -> list[DTO]`
    - `update(self, dto: DTO, **filters) -> DTO | None`
    - `delete(self, **filters) -> bool`

    ### Usage Example:
    ```python
    # @use_collection(db["users"])
    class UserRepository(BaseMongoRepository[UserDTO]):
        class Meta:
            # dto = UserDTO
            collection = db["users"]
            index = mongorepo.Index(field="username")

    repo = UserRepository()

    # Adding a user
    user = repo.add(UserDTO(username="john_doe"))

    # Retrieving a user
    retrieved_user = repo.get(username="john_doe")
    ```

    Raises:
        - `NoDTOTypeException`: If no DTO type is provided in the `Meta` class or in generic.
        - `NoCollectionException`: If an index is specified but no collection is provided
          in the `Meta` class.

    """

    def __new__(cls, *args, **kwargs) -> 'BaseMongoRepository[DTO]':
        instance = super().__new__(cls)
        try:
            dto_type = _get_dto_from_origin(cls)
        except exceptions.NoDTOTypeException:
            dto_type = None

        try:
            meta: MetaAttributes[Collection] | None = _get_meta_attributes(cls)
        except exceptions.NoMetaException:
            meta = None

        id_field: str | None = meta['id_field'] if meta else None

        if dto_type is None:
            dto_type = meta['dto'] if meta else None
            if not dto_type:
                raise exceptions.NoDTOTypeException

        collection: Collection | None = meta['collection'] if meta else None
        index: Index | str | None = meta['index'] if meta else None

        if index is not None:
            if collection is None:
                raise exceptions.NoCollectionException(
                    message='Index can be created only if collection provided in Meta class',
                )
            _create_index(index, collection=collection)
        converter = _get_converter(dto_type, id_field)

        add_method = AddMethod(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        add_batch_method = AddBatchMethod(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        get_method = GetMethod(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        get_list_method = GetListMethod(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        get_all_method = GetAllMethod(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        update_method = UpdateMethod(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        delete_method = DeleteMethod(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa

        if hasattr(cls, '__mongorepo__'):
            __mongorepo__: MongorepoDict[ClientSession, Collection] = getattr(cls, '__mongorepo__')
            __mongorepo__['methods']['add'] = add_method
            __mongorepo__['methods']['add_batch'] = add_batch_method
            __mongorepo__['methods']['get'] = get_method
            __mongorepo__['methods']['get_list'] = get_list_method
            __mongorepo__['methods']['get_all'] = get_all_method
            __mongorepo__['methods']['update'] = update_method
            __mongorepo__['methods']['delete'] = delete_method
        else:
            __mongorepo__ = MongorepoDict[ClientSession, Collection](
                collection_provider=CollectionProvider(obj=cls, collection=collection),
                methods={
                    'add': add_method,
                    'add_batch': add_batch_method,
                    'get': get_method,
                    'get_list': get_list_method,
                    'get_all': get_all_method,
                    'update': update_method,
                    'delete': delete_method,
                },
            )
            cls.__mongorepo__ = __mongorepo__

        setattr(cls, '_mongorepo_add', __mongorepo__['methods']['add'])
        setattr(cls, '_mongorepo_add_batch', __mongorepo__['methods']['add_batch'])
        setattr(cls, '_mongorepo_get', __mongorepo__['methods']['get'])
        setattr(cls, '_mongorepo_get_list', __mongorepo__['methods']['get_list'])
        setattr(cls, '_mongorepo_get_all', __mongorepo__['methods']['get_all'])
        setattr(cls, '_mongorepo_update', __mongorepo__['methods']['update'])
        setattr(cls, '_mongorepo_delete', __mongorepo__['methods']['delete'])

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
    """## Base Asynchronous MongoDB Repository

    This class provides a foundation for creating asynchronous repositories using MongoDB.
    It dynamically extends child classes with various CRUD
    operations and integrates with MongoDB collections.

    ### Features:
    - **Automatic method injection**: Methods like `add`, `get`, `update`, and `delete`
    are dynamically attached.
    - **Asynchronous support**: Utilizes `AsyncIOMotorCollection` for non-blocking
    database operations.
    - **Index creation**: Supports indexing using `mongorepo.Index` or a simple field name.
    - **DTO-based operations**: Ensures type safety with a provided Data Transfer Object (DTO).
    - **Meta class support**: The child class can define a `Meta` class with:
      - `dto`: A dataclass representing the document structure.
      - `collection`: An instance of `AsyncIOMotorCollection` representing the MongoDB collection.
      - `index` (optional): Defines an index for efficient querying.
    ### Required:
    - **Collection**: provide collection of type `AsyncIOMotorCollection` either in `Meta` class or
    with `mongorepo.use_collection` decorator
    - **DTO**: provide DTO type in Generic
    (e.g. `class Repo(BaseAsyncMongoRepository[MyDataclass])`) or in `Meta` class

    ### Available Methods:
    - `add(self, dto: DTO) -> DTO`
    - `add_batch(self, dto_list: list[DTO]) -> InsertManyResult`
    - `get(self, **filters) -> DTO | None`
    - `get_all(self, **filters) -> AsyncGenerator[DTO, None]`
    - `get_list(self, offset: int = 0, limit: int = 20, **filters) -> list[DTO]`
    - `update(self, dto: DTO, **filters) -> DTO | None`
    - `delete(self, **filters) -> bool`

    ### Usage Example:
    ```python
    # @use_collection(db["users"])
    class UserRepository(BaseAsyncMongoRepository[UserDTO]):
        class Meta:
            # dto = UserDTO
            collection = db["users"]
            index = mongorepo.Index(field="username")

    repo = UserRepository()

    # Adding a user
    user = await repo.add(UserDTO(username="john_doe"))

    # Retrieving a user
    retrieved_user = await repo.get(username="john_doe")
    ```

    Raises:
        - `NoDTOTypeException`: If no DTO type is provided in the `Meta` class or in generic.
        - `NoCollectionException`: If an index is specified but no collection is provided
        in `Meta` class.

    """

    def __new__(cls, *args, **kwargs) -> 'BaseAsyncMongoRepository[DTO]':
        instance = super().__new__(cls)
        try:
            dto_type = _get_dto_from_origin(cls)
        except exceptions.NoDTOTypeException:
            dto_type = None

        try:
            meta: MetaAttributes[AsyncIOMotorCollection] | None = _get_meta_attributes(cls)
        except exceptions.NoMetaException:
            meta = None

        id_field: str | None = meta['id_field'] if meta else None

        if dto_type is None:
            dto_type = meta['dto'] if meta else None
            if not dto_type:
                raise exceptions.NoDTOTypeException

        collection: AsyncIOMotorCollection | None = meta['collection'] if meta else None
        index: Index | str | None = meta['index'] if meta else None

        if index is not None:
            if collection is None:
                raise exceptions.NoCollectionException(
                    message='Index can be created only if collection provided in Meta class',
                )
            asyncio.create_task(_create_index_async(index, collection=collection))
        converter = _get_converter(dto_type, id_field)

        add_method = AddMethodAsync(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        add_batch_method = AddBatchMethodAsync(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        get_method = GetMethodAsync(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        get_list_method = GetListMethodAsync(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        get_all_method = GetAllMethodAsync(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        update_method = UpdateMethodAsync(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa
        delete_method = DeleteMethodAsync(dto_type, cls, id_field=id_field, converter=converter)  # type: ignore  # noqa

        if hasattr(cls, '__mongorepo__'):
            __mongorepo__: MongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection] = getattr(cls, '__mongorepo__')  # noqa
            __mongorepo__['methods']['add'] = add_method
            __mongorepo__['methods']['add_batch'] = add_batch_method
            __mongorepo__['methods']['get'] = get_method
            __mongorepo__['methods']['get_list'] = get_list_method
            __mongorepo__['methods']['get_all'] = get_all_method
            __mongorepo__['methods']['update'] = update_method
            __mongorepo__['methods']['delete'] = delete_method
        else:
            __mongorepo__ = MongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection](
                collection_provider=CollectionProvider(obj=cls, collection=collection),
                methods={
                    'add': add_method,
                    'add_batch': add_batch_method,
                    'get': get_method,
                    'get_list': get_list_method,
                    'get_all': get_all_method,
                    'update': update_method,
                    'delete': delete_method,
                },
            )
            cls.__mongorepo__ = __mongorepo__

        setattr(cls, '_mongorepo_add', __mongorepo__['methods']['add'])
        setattr(cls, '_mongorepo_add_batch', __mongorepo__['methods']['add_batch'])
        setattr(cls, '_mongorepo_get', __mongorepo__['methods']['get'])
        setattr(cls, '_mongorepo_get_list', __mongorepo__['methods']['get_list'])
        setattr(cls, '_mongorepo_get_all', __mongorepo__['methods']['get_all'])
        setattr(cls, '_mongorepo_update', __mongorepo__['methods']['update'])
        setattr(cls, '_mongorepo_delete', __mongorepo__['methods']['delete'])

        return instance

    async def get(self, **filters: Any) -> DTO | None:
        return await self.__class__._mongorepo_get(**filters)  # type: ignore

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
