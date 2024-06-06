from dataclasses import asdict, is_dataclass
from typing import Any, Generic, Iterable

from pymongo.collection import Collection

from mongorepo.utils import _create_index, _get_dto_type_from_origin, _get_meta_attributes
from mongorepo.base import DTO, Index
from mongorepo import exceptions


class BaseMongoRepository(Generic[DTO]):
    """
    ### Base repository class
    #### Extend child class with various methods:
    ```
    add(self, dto: DTO) -> DTO
    get(self, _id: str | None = None, **filters) -> DTO | None
    get_all(self, **filters) -> Iterable[DTO]
    update(self, dto: DTO, **filter_) -> DTO
    delete(self, _id: str | None = None, **filters) -> bool
    ```
    Provide DTO type in type hints, example:
    ```
    class DummyMongoRepository(MongoRepository[UserDTO]):
        ...
    ```
    If you want to create an index use mongorepo.Index or just a name of the field to put string on
    ```
    def __init__(
        self,
        collection: pymongo.Collection | None = None,
        index: mongorepo.Index | str | None = None
    ) -> None:
    ```
    """
    def __init__(
        self,
        collection: Collection | None = None,
        index: Index | str | None = None,
    ) -> None:
        self.collection = self.__get_collection(collection)
        self.dto_type = _get_dto_type_from_origin(self.__class__)
        if not is_dataclass(self.dto_type):
            raise exceptions.NotDataClass
        if index is not None:
            _create_index(index, collection=self.collection)

    @classmethod
    def __get_collection(cls, collection: Collection | None) -> Collection:
        if collection is not None:
            return collection
        try:
            attrs = _get_meta_attributes(cls, raise_exceptions=False)
        except exceptions.NoMetaException:
            raise exceptions.MongoRepoException(
                '"Meta" class with "collecton" was not defined in the class'
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

    def get(self, _id: str | None = None, **filters: Any) -> DTO | None:
        if _id is not None:
            filters['_id'] = _id
        result = self.collection.find_one(filters)
        if not result:
            return None
        return self._convert_to_dto(result)  # type: ignore

    def get_all(self, **filters: Any) -> Iterable[DTO]:
        cursor = self.collection.find(filters)
        for doc in cursor:
            yield self._convert_to_dto(doc)

    def update(self, dto: DTO, **filter_: Any) -> DTO:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():  # type: ignore
            if isinstance(value, (int, bool, float)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        self.collection.find_one_and_update(filter=filter_, update=data)
        return dto

    def delete(self, _id: str | None = None, **filters: Any) -> bool:
        if _id is not None:
            filters['_id'] = _id
        deleted = self.collection.find_one_and_delete(filters)
        if deleted is not None:
            return True
        return False

    def add(self, dto: DTO) -> DTO:
        self.collection.insert_one(asdict(dto))  # type: ignore
        return dto
