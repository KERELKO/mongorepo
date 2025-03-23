from abc import ABC, abstractmethod

import mongorepo
from mongorepo import BaseMongoRepository
from mongorepo._collections import use_collection
from mongorepo.implements.methods import (
    AddMethod,
    FieldAlias,
    GetMethod,
    ListAppendMethod,
    ListRemoveMethod,
)
from tests.common import Box, MixDTO, SimpleDTO, in_collection


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

        @use_collection(coll)
        @mongorepo.implements(
            AbstractRepository,
            GetMethod(AbstractRepository.get_my_dto, filters=['x']),
            AddMethod(AbstractRepository.add_new, dto='dto'),
        )
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


def test_array_fields():
    with in_collection(MixDTO) as coll:
        @mongorepo.repository(array_fields=('records', 'boxs'))
        class Repository:
            class Meta:
                dto = MixDTO
                collection = coll

        repo = Repository()
        dto = MixDTO(
            id='1',
            name='box',
            year=2025,
            main_box=Box(id='1', value='box'),
            records=[1, 2, 3],
            boxs=[Box('2', '2')],
        )
        repo.add(dto)  # type: ignore

        repo.records__append(value=5, id='1')  # type: ignore
        repo.boxs__append(value=Box('3', '3'), id='1')  # type: ignore
        get_dto: MixDTO | None = repo.get(id='1')  # type: ignore
        assert get_dto is not None
        assert get_dto.records[-1] == 5
        assert get_dto.boxs[-1] == Box('3', '3')

        repo.records__remove(value=2, id='1')  # type: ignore
        repo.boxs__remove(value=Box('2', '2'), id='1')  # type: ignore
        get_dto: MixDTO | None = repo.get(id='1')  # type: ignore
        assert get_dto is not None
        assert 2 not in get_dto.records
        assert Box('2', '2') not in get_dto.boxs


def test_array_fields_with_implements():
    with in_collection(MixDTO) as coll:
        class AbstractRepository(ABC):
            @abstractmethod
            def add(self, mix: MixDTO):
                ...

            @abstractmethod
            def get(self, id: str) -> MixDTO | None:
                ...

            @abstractmethod
            def add_box(self, mix_id: str, box: Box):
                ...

            @abstractmethod
            def remove_box(self, mix_id: str, box: Box):
                ...

        @mongorepo.implements(
            AbstractRepository,
            GetMethod(AbstractRepository.get, filters=['id']),
            AddMethod(AbstractRepository.add, dto='mix'),
            ListAppendMethod(
                AbstractRepository.add_box,
                field_name='boxs',
                value='box',
                filters=[FieldAlias('id', 'mix_id')],
            ),
            ListRemoveMethod(
                AbstractRepository.remove_box,
                field_name='boxs',
                value='box',
                filters=[FieldAlias('id', 'mix_id')],
            ),
        )
        class Repository:
            class Meta:
                dto = MixDTO
                collection = coll

        repo: AbstractRepository = Repository()  # type: ignore
        dto = MixDTO(
            id='1',
            name='box',
            year=2025,
            main_box=Box(id='1', value='box'),
            records=[1, 2, 3],
            boxs=[Box('2', '2')],
        )
        repo.add(dto)
        repo.add_box(box=Box('3', '3'), mix_id='1')
        get_dto = repo.get(id='1')
        assert get_dto is not None
        assert get_dto.records[-1] == 3
        assert get_dto.boxs[-1] == Box('3', '3')
