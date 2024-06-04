from dataclasses import asdict
from typing import Any, AsyncGenerator, Generic, TypeVar, get_args

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from mongorepo.base import DTO


class AsyncBasedMongoRepository(Generic[DTO]):
    """
    ### Asynchronous base repository class,
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
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection: AsyncIOMotorCollection = collection
        self.dto_type = self.__get_origin()

    @classmethod
    def __get_origin(cls) -> type:
        dto_type = get_args(cls.__orig_bases__[0])[0]  # type: ignore
        if isinstance(dto_type, TypeVar):
            raise AttributeError('"DTO type" was not provided in the class declaration')
        return dto_type

    def _convert_to_dto(self, dct: dict[str, Any]) -> DTO:
        if hasattr(self.dto_type, '_id'):
            return self.dto_type(**dct)
        dct.pop('_id')
        return self.dto_type(**dct)

    async def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        result = await self.collection.find_one(filters)
        if not result:
            return None
        return self._convert_to_dto(result)  # type: ignore

    async def get_all(self, **filters: Any) -> AsyncGenerator[DTO, None]:
        cursor = self.collection.find(filters)
        async for doc in cursor:
            yield self._convert_to_dto(doc)

    async def update(self, dto: DTO, **filter_: Any) -> DTO:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():  # type: ignore
            if isinstance(value, (int, bool)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        await self.collection.find_one_and_update(filter=filter_, update=data)
        return dto

    async def delete(self, _id: str | None = None, **filters: Any) -> bool:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        deleted = await self.collection.find_one_and_delete(filters)
        if deleted is not None:
            return True
        return False

    async def create(self, dto: DTO) -> DTO:
        await self.collection.insert_one(asdict(dto))  # type: ignore
        return dto
