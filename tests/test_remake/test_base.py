from abc import ABC, abstractmethod

import mongorepo
from mongorepo import BaseMongoRepository
from mongorepo._base import MONGOREPO_COLLECTION  # noqa
from mongorepo._collections import use_collection
from mongorepo.implements.methods import AddMethod, GetMethod
from tests.common import SimpleDTO, in_collection


def test_mongorepo_respoitory():
    with in_collection(SimpleDTO) as coll:
        @mongorepo.repository(add=True, get=True)
        class Repository:
            class Meta:
                collection = coll
                dto = SimpleDTO

        repo = Repository()
        dto = SimpleDTO(x='123', y=123)
        added_dto = repo.add(dto)  # type: ignore
        assert added_dto is not None
        assert added_dto.x == '123'

        get_dto = repo.get(x='123')  # type: ignore
        assert get_dto is not None
        assert get_dto.y == 123


def test_mongorepo_respoitory_with_use_collection():
    with in_collection(SimpleDTO) as coll:
        @use_collection(coll)
        @mongorepo.repository(add=True, get=True)
        class Repository:
            class Meta:
                dto = SimpleDTO

        repo = Repository()
        dto = SimpleDTO(x='123', y=123)
        added_dto = repo.add(dto)  # type: ignore
        assert added_dto is not None
        assert added_dto.x == '123'

        get_dto = repo.get(x='123')  # type: ignore
        assert get_dto is not None
        assert get_dto.y == 123


def test_mongorepo_class():
    with in_collection(SimpleDTO) as coll:
        class Repository(BaseMongoRepository[SimpleDTO]):
            class Meta:
                collection = coll

        repo = Repository()
        dto = SimpleDTO(x='123', y=123)
        added_dto = repo.add(dto)
        assert added_dto is not None
        assert added_dto.x == '123'

        get_dto = repo.get(x='123')
        assert get_dto is not None
        assert get_dto.y == 123


def test_mongorepo_class_with_use_collection():
    with in_collection(SimpleDTO) as coll:

        @use_collection(coll)
        class Repository(BaseMongoRepository[SimpleDTO]):
            ...

        repo = Repository()
        dto = SimpleDTO(x='123', y=123)
        added_dto = repo.add(dto)
        assert added_dto is not None
        assert added_dto.x == '123'

        get_dto = repo.get(x='123')
        assert get_dto is not None
        assert get_dto.y == 123


def test_implements():
    with in_collection(SimpleDTO) as coll:

        class AbstractRepository(ABC):
            @abstractmethod
            def get_my_dto(self, x: str) -> SimpleDTO | None:
                ...

            @abstractmethod
            def add_new(self, dto: SimpleDTO):
                ...

        @mongorepo.implements(
            AbstractRepository,
            GetMethod(AbstractRepository.get_my_dto, filters=['x']),
            AddMethod(AbstractRepository.add_new, dto='dto'),
        )
        @use_collection(coll)
        class Repository:
            class Meta:
                dto = SimpleDTO

        repo: AbstractRepository = Repository()  # type: ignore
        dto = SimpleDTO(x='123', y=123)
        added_dto = repo.add_new(dto)
        assert added_dto is not None
        assert added_dto.x == '123'

        get_dto = repo.get_my_dto(x='123')
        assert get_dto is not None
        assert get_dto.y == 123
