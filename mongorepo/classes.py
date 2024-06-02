from dataclasses import asdict, dataclass
from typing import Generic, Iterable, Type

from bson import ObjectId
from pymongo.collection import Collection

from mongorepo.base import DTO


@dataclass(repr=False, eq=False)
class MongoRepository(Generic[DTO]):
    """
    ### Base repository class, extend child class with various methods:
    ```
    create(self, dto: DTO) -> DTO
    get(self, _id: str | None = None, **filters) -> DTO | None
    get_all(self, **filters) -> Iterable[DTO]
    update(self, dto: DTO, **filter_) -> DTO
    delete(self, _id: str | None = None, **filters) -> bool
    ```
    """
    dto_type: Type[DTO]
    collection: Collection

    def get(self, _id: str | None = None, **filters) -> DTO | None:
        if _id is not None:
            oid = ObjectId(_id)
        filters['_id'] = oid
        result = self.collection.find_one(filters)
        if not result:
            return None
        result.pop('_id')
        return self.dto_type(**result)

    def get_all(self, **filters) -> Iterable[DTO]:
        """
        Returns Generator of found items
        ```
        gen = repo.get_all(username='admin')
        for item in gen:
            ...
        ```
        """
        cursor = self.collection.find(filters)
        for dto in cursor:
            yield dto

    def update(self, dto: DTO, **filter_) -> DTO:
        data = {'$set': {}}
        for field, value in asdict(dto).items():  # type: ignore
            if isinstance(value, (int, bool)):
                data['$set'][field] = value
            elif not field:
                continue
            data['$set'][field] = value
        self.collection.find_one_and_update(filter=filter_, update=data)
        return dto

    def delete(self, _id: str | None = None, **filters) -> bool:
        if _id is not None:
            filters['_id'] = ObjectId(_id)
        deleted = self.collection.find_one_and_delete(filters)
        if deleted is not None:
            return True
        return False

    def create(self, dto: DTO) -> DTO:
        self.collection.insert_one(asdict(dto))  # type: ignore
        return dto
