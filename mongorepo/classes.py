from dataclasses import asdict
from typing import Any, Generic, Iterable, TypeVar, get_args

from bson import ObjectId
from pymongo.collection import Collection

from mongorepo.base import DTO


class BaseMongoRepository(Generic[DTO]):
    """
    ### Base repository class,
    Provide DTO type in type hints, example:
    ```
    class DummyMongoRepository(MongoRepository[UserDTO]):
        ...
    ```
    #### Extend child class with various methods:
    ```
    create(self, dto: DTO) -> DTO
    get(self, _id: str | None = None, **filters) -> DTO | None
    get_all(self, **filters) -> Iterable[DTO]
    update(self, dto: DTO, **filter_) -> DTO
    delete(self, _id: str | None = None, **filters) -> bool
    ```
    """
    def __init__(self, collection: Collection) -> None:
        self.collection: Collection = collection
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

    def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        result = self.collection.find_one(filters)
        if not result:
            return None
        return self._convert_to_dto(result)  # type: ignore

    def get_all(self, **filters: Any) -> Iterable[DTO]:
        cursor = self.collection.find(filters)
        for doc in cursor:
            yield self._convert_to_dto(doc)

    def update(self, dto: DTO, **filter_: Any) -> DTO:
        data = {'$set': {}}
        for field, value in asdict(dto).items():  # type: ignore
            if isinstance(value, (int, bool)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        self.collection.find_one_and_update(filter=filter_, update=data)
        return dto

    def delete(self, _id: str | None = None, **filters: Any) -> bool:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        deleted = self.collection.find_one_and_delete(filters)
        if deleted is not None:
            return True
        return False

    def create(self, dto: DTO) -> DTO:
        self.collection.insert_one(asdict(dto))  # type: ignore
        return dto
