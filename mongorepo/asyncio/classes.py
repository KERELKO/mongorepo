from dataclasses import asdict, is_dataclass
from typing import Any, AsyncGenerator, Generic

from motor.motor_asyncio import AsyncIOMotorCollection

from mongorepo import exceptions
from mongorepo.base import DTO, Index
from mongorepo.utils import _get_dto_type_from_origin, _get_meta_attributes


class AsyncBasedMongoRepository(Generic[DTO]):
    """
    ## Asynchronous base repository class,
    Provide DTO type in type hints, example:
    ```
    class DummyMongoRepository(AsyncBasedMongoRepository[UserDTO]):
        ...
    ```
    #### Extend child class with various methods:
    ```
    async create(self, dto: DTO) -> DTO
    async get(self, _id: str | None = None, **filters) -> DTO | None
    async get_all(self, **filters) -> Iterable[DTO]
    async update(self, dto: DTO, **filter_) -> DTO
    async delete(self, _id: str | None = None, **filters) -> bool
    ```
    """
    def __init__(
        self,
        collection: AsyncIOMotorCollection | None = None,
        index: Index | str | None = None,
    ) -> None:
        self.collection = self.__get_collection(collection)

        self.dto_type = _get_dto_type_from_origin(self.__class__)
        if not is_dataclass(self.dto_type):
            raise exceptions.NotDataClass

        self.__set_index(index)

    def __set_index(self, index: Index | None | str) -> None:
        if index is None:
            attrs = _get_meta_attributes(self.__class__, raise_exceptions=False)
        index = attrs['index']
        if index is not None:
            ...
            # async_to_sync(_create_index_async(index, collection=self.collection))  # type: ignore

    @classmethod
    def __get_collection(cls, collection: AsyncIOMotorCollection | None) -> AsyncIOMotorCollection:
        if collection is not None:
            return collection
        try:
            attrs = _get_meta_attributes(cls, raise_exceptions=False)
        except exceptions.NoMetaException:
            raise exceptions.MongoRepoException(
                '"Meta" class with "collection" was not defined in the class'
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

    async def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        if _id is not None:
            filters['_id'] = _id
        result = await self.collection.find_one(filters)
        if not result:
            return None
        return self._convert_to_dto(result)

    async def get_all(self, **filters: Any) -> AsyncGenerator[DTO, None]:
        cursor = self.collection.find(filters)
        async for doc in cursor:
            yield self._convert_to_dto(doc)

    async def update(self, dto: DTO, **filter_: Any) -> DTO:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():
            if isinstance(value, (int, bool)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        await self.collection.find_one_and_update(filter=filter_, update=data)
        return dto

    async def delete(self, _id: str | None = None, **filters: Any) -> bool:
        if _id is not None:
            filters['_id'] = _id
        deleted = await self.collection.find_one_and_delete(filters)
        if deleted is not None:
            return True
        return False

    async def add(self, dto: DTO) -> DTO:
        await self.collection.insert_one(asdict(dto))
        return dto
