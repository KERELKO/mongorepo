from dataclasses import asdict
from typing import Any, AsyncGenerator, Generic

from motor.motor_asyncio import AsyncIOMotorCollection

from mongorepo.asyncio._methods import _add_method_async
from mongorepo import exceptions
from mongorepo import DTO, Index
from mongorepo.utils import (
    _get_converter,
    _get_dto_from_origin,
    _get_meta_attributes,
    _get_collection_and_dto,
)
from mongorepo.asyncio.utils import _run_asyncio_create_index


class AsyncBasedMongoRepository(Generic[DTO]):
    """
    ## Asynchronous base repository class,
    #### Provide DTO type in type hints, example:
    ```
    class DummyMongoRepository(AsyncBasedMongoRepository[UserDTO]):
        ...
    ```
    #### Extend child classes with various methods:
    ```
    async create(self, dto: DTO) -> DTO
    async get(self, **filters) -> DTO | None
    async get_all(self, **filters) -> Iterable[DTO]
    async update(self, dto: DTO, **filters) -> DTO
    async delete(self, **filters) -> bool
    ```
    """

    def __new__(cls, *args, **kwargs) -> 'AsyncBasedMongoRepository':
        instance = super().__new__(cls)
        setattr(instance, 'dto_type',  _get_dto_from_origin(cls))

        try:
            meta = _get_meta_attributes(cls, raise_exceptions=False)
        except exceptions.NoMetaException:
            meta = None

        index: Index | str | None = meta['index'] if meta else None
        id_field: str | None = meta['id_field'] if meta else None

        setattr(instance, '__convert_to_dto', _get_converter(id_field=id_field))
        setattr(instance, '__id_field', id_field)

        if index is not None:
            collection: AsyncIOMotorCollection | None = meta['collection'] if meta else None
            if collection is None:
                raise exceptions.NoCollectionException(
                    message='Cannot access collection from Meta, to create index'
                )
            _run_asyncio_create_index(index, collection=collection)
        return instance

    def __init__(self, collection: AsyncIOMotorCollection | None = None) -> None:
        self.collection = self.__get_collection(collection)
        self.__convert_to_dto_func = self.__dict__['__convert_to_dto']
        self._add_func = _add_method_async(
            dto_type=self.dto_type,  # type: ignore
            collection=self.collection,
            id_field=self.__dict__['__id_field']
        )
        if 'dto_type' not in self.__dict__:
            self.dto_type = _get_dto_from_origin(self.__class__)

    @classmethod
    def __get_collection(cls, collection: AsyncIOMotorCollection | None) -> AsyncIOMotorCollection:
        if collection is not None:
            return collection
        try:
            attrs = _get_collection_and_dto(cls, raise_exceptions=False)
        except exceptions.NoMetaException:
            raise exceptions.MongoRepoException(
                message='"Meta" class with "collection" variable was not defined in the class'
            )
        if attrs['collection'] is None:
            raise exceptions.NoCollectionException
        defined_collection = attrs['collection']
        return defined_collection

    def _convert_to_dto(self, dct: dict[str, Any]) -> DTO:
        return self.__convert_to_dto_func(self.dto_type, dct)

    async def get(self, **filters: Any) -> DTO | None:
        result = await self.collection.find_one(filters)
        return self._convert_to_dto(result) if result else None

    async def get_all(self, **filters: Any) -> AsyncGenerator[DTO, None]:
        cursor = self.collection.find(filters)
        async for doc in cursor:
            yield self._convert_to_dto(doc)

    async def update(self, dto: DTO, **filters: Any) -> DTO | None:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():
            if isinstance(value, (int, bool)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        update_doc = await self.collection.find_one_and_update(
            filter=filters, update=data, return_document=True,
        )
        return self._convert_to_dto(update_doc) if update_doc else None

    async def delete(self, **filters: Any) -> bool:
        deleted = await self.collection.find_one_and_delete(filters)
        return True if deleted else False

    async def add(self, dto: DTO) -> DTO:
        return await self._add_func(self, dto)  # type: ignore
