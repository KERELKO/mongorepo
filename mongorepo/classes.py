from dataclasses import asdict, is_dataclass
from typing import Any, Generic, Iterable, Protocol

from pymongo.collection import Collection

from mongorepo.utils import create_index, _get_dto_from_origin, _get_meta_attributes
from mongorepo import DTO, Index
from mongorepo import exceptions


class IMongoRepository(Protocol[DTO]):
    def get(self, **filters: Any) -> DTO | None:
        raise NotImplementedError

    def get_all(self, **filters: Any) -> Iterable[DTO]:
        raise NotImplementedError

    def update(self, dto: DTO, **filters: Any) -> DTO:
        raise NotImplementedError

    def delete(self, **filters: Any) -> bool:
        raise NotImplementedError

    def add(self, dto: DTO) -> DTO:
        raise NotImplementedError


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

    def __new__(cls, *args, **kwargs) -> 'BaseMongoRepository':
        try:
            meta = _get_meta_attributes(cls, raise_exceptions=False)
        except exceptions.NoMetaException:
            return super().__new__(cls)
        index: Index | str | None = meta['index']
        if index is not None:
            collection: Collection | None = meta['collection']
            if collection is None:
                raise exceptions.NoCollectionException(
                    message='Cannot access collection from Meta, to create index'
                )
            cls.collection = collection
            create_index(index=index, collection=collection)

        cls.dto_type = _get_dto_from_origin(cls)
        if not is_dataclass(cls.dto_type):
            raise exceptions.NotDataClass

        return super().__new__(cls)

    def __init__(self, collection: Collection | None = None) -> None:
        self.collection = self.__get_collection(collection)
        self.dto_type = _get_dto_from_origin(self.__class__)

    @classmethod
    def __get_collection(cls, collection: Collection | None) -> Collection:
        if collection is not None:
            return collection
        try:
            attrs = _get_meta_attributes(cls, raise_exceptions=False)
        except exceptions.NoMetaException:
            raise exceptions.MongoRepoException(
                message='"Meta" class with "collecton" was not defined in the class'
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

    def get(self, **filters: Any) -> DTO | None:
        result = self.collection.find_one(filters)
        return self._convert_to_dto(result) if result else None

    def get_all(self, **filters: Any) -> Iterable[DTO]:
        cursor = self.collection.find(filters)
        for doc in cursor:
            yield self._convert_to_dto(doc)

    def update(self, dto: DTO, **filters: Any) -> DTO:
        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in asdict(dto).items():
            if isinstance(value, (int, bool, float)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        self.collection.find_one_and_update(filter=filters, update=data)
        return dto

    def delete(self, **filters: Any) -> bool:
        """Returns True if document was deleted else False"""
        deleted = self.collection.find_one_and_delete(filters)
        return True if deleted else False

    def add(self, dto: DTO) -> DTO:
        self.collection.insert_one(asdict(dto))
        return dto
