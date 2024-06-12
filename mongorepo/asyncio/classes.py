from dataclasses import asdict, is_dataclass
from typing import Any, AsyncGenerator, Generic

from motor.motor_asyncio import AsyncIOMotorCollection

from mongorepo import exceptions
from mongorepo import DTO, Index
from mongorepo.utils import _get_dto_from_origin, _get_meta_attributes
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

    def __new__(cls) -> 'AsyncBasedMongoRepository':
        try:
            meta = _get_meta_attributes(cls, raise_exceptions=False)
        except exceptions.NoMetaException:
            return super().__new__(cls)
        index: Index | str | None = meta['index']
        if index is not None:
            collection: AsyncIOMotorCollection | None = meta['collection']
            if collection is None:
                raise exceptions.NoCollectionException(
                    message='Cannot access collection from Meta, to create index'
                )
            cls.collection = collection
            _run_asyncio_create_index(index, collection=collection)

        cls.dto_type = _get_dto_from_origin(cls)
        if not is_dataclass(cls.dto_type):
            raise exceptions.NotDataClass

        return super().__new__(cls)

    def __init__(self, collection: AsyncIOMotorCollection | None = None) -> None:
        self.collection = self.__get_collection(collection)
        self.dto_type = _get_dto_from_origin(self.__class__)

    @classmethod
    def __get_collection(cls, collection: AsyncIOMotorCollection | None) -> AsyncIOMotorCollection:
        if collection is not None:
            return collection
        try:
            attrs = _get_meta_attributes(cls, raise_exceptions=False)
        except exceptions.NoMetaException:
            raise exceptions.MongoRepoException(
                message='"Meta" class with "collection" variable was not defined in the class'
            )
        if attrs['collection'] is None:
            raise exceptions.NoCollectionException
        defined_collection = attrs['collection']
        return defined_collection

    def _convert_to_dto(self, dct: dict[str, Any]) -> DTO:
        if hasattr(self.dto_type, '_id'):
            return self.dto_type(**dct)
        dct.pop('_id')
        return self.dto_type(**dct)

    async def get(self, **filters: Any) -> DTO | None:
        result = await self.collection.find_one(filters)
        return self._convert_to_dto(result) if result else None

    async def get_all(self, **filters: Any) -> AsyncGenerator[DTO, None]:
        cursor = self.collection.find(filters)
        async for doc in cursor:
            yield self._convert_to_dto(doc)

    async def update(self, dto: DTO, **filters: Any) -> DTO:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():
            if isinstance(value, (int, bool)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        await self.collection.find_one_and_update(filter=filters, update=data)
        return dto

    async def delete(self, **filters: Any) -> bool:
        deleted = await self.collection.find_one_and_delete(filters)
        return True if deleted else False

    async def add(self, dto: DTO) -> DTO:
        await self.collection.insert_one(asdict(dto))
        return dto
