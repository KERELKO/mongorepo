import random
from typing import Generic

import pytest

from mongorepo import DTO, Index, use_collection
from mongorepo.classes import BaseMongoRepository
from mongorepo.exceptions import NoDTOTypeException
from tests.common import ComplicatedDTO, DTOWithID, SimpleDTO, in_collection


def test_all_methods_with_inherited_repo():

    with in_collection(SimpleDTO) as coll:
        @use_collection(coll)
        class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
            ...

        num = random.randint(1, 12346)
        unum = random.randint(1, 4567)
        repo = TestMongoRepository()

        new_dto = repo.add(SimpleDTO(x='hey', y=num))
        assert new_dto.x == 'hey'

        updated_dto = repo.update(SimpleDTO(x='hey all!', y=unum), y=num)
        assert updated_dto is not None
        assert updated_dto.x == 'hey all!'

        for selected_dto in repo.get_all():
            assert selected_dto.x == 'hey all!'
            break

        dto = repo.get(y=unum)
        assert dto is not None

        is_deleted = repo.delete(y=unum)
        assert is_deleted is True

        dto = repo.get(y=unum)
        assert dto is None

        batch = [SimpleDTO(x='1', y=1), SimpleDTO(x='2', y=2), SimpleDTO(x='3', y=3)]
        repo.add_batch(batch)

        get_list = repo.get_list()
        assert len(get_list) == 3

        added = [1, 2, 3]
        for dto in repo.get_all():
            assert dto.y in added


def test_can_get_dto_with_id():

    with in_collection(DTOWithID) as coll:
        @use_collection(coll)
        class TestMongoRepository(BaseMongoRepository[DTOWithID]):
            ...

        num = random.randint(1, 12346)
        repo = TestMongoRepository()

        new_dto = repo.add(DTOWithID(x='dto with id', y=num))
        assert new_dto.x == 'dto with id'

        dto: DTOWithID = repo.get(y=num)  # type: ignore
        assert dto._id is not None


def test_can_handle_complicated_dto():

    with in_collection(ComplicatedDTO) as coll:
        @use_collection(coll)
        class TestMongoRepository(BaseMongoRepository[ComplicatedDTO]):
            ...

        repo = TestMongoRepository()

        repo.add(ComplicatedDTO(x='comp', y=True, name='You', skills=['h', 'e']))

        resolved_dto = repo.get(name='You')
        assert resolved_dto.skills == ['h', 'e'] and resolved_dto.x == 'comp'  # type: ignore


def test_can_update_partially():

    with in_collection(ComplicatedDTO) as coll:
        @use_collection(coll)
        class TestMongoRepository(BaseMongoRepository[ComplicatedDTO]):
            ...

        repo = TestMongoRepository()

        repo.add(ComplicatedDTO(x='Test', y=True, name='Me'))
        repo.update(name='Me', dto=ComplicatedDTO(x='Test', skills=['hello!'], name='Me'))

        updated_dto = repo.get(name='Me')
        assert updated_dto.skills == ['hello!']  # type:ignore


def test_can_search_with_id():

    with in_collection(DTOWithID) as coll:
        class TestMongoRepository(BaseMongoRepository):
            class Meta:
                dto = DTOWithID
                collection = coll

        repo = TestMongoRepository()

        dto_id = repo.add(DTOWithID(x='ID', y=23450))._id

        dto: DTOWithID = repo.get(_id=dto_id)  # type: ignore
        assert dto.x == 'ID'


def test_can_add_index():
    with in_collection(SimpleDTO) as coll:
        _index = Index(field='y', name='y_index', desc=True, unique=False)

        class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
            class Meta:
                index = _index
                collection = coll

        _ = TestMongoRepository()

        assert 'y_index' in coll.index_information()


def test_can_access_dto_type_in_type_hints_class_repo():

    with in_collection(SimpleDTO) as coll:
        class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
            ...

        _ = TestMongoRepository(coll)


def test_cannot_access_dto_type_in_type_hints_class():
    with in_collection(SimpleDTO) as coll:
        with pytest.raises(NoDTOTypeException):
            class TestMongoRepository(BaseMongoRepository):
                ...

            _ = use_collection(coll)(TestMongoRepository)()


def test_move_collection_init_to_meta_in_class_repo():
    with in_collection(SimpleDTO) as coll:
        class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
            class Meta:
                collection = coll

        repo = TestMongoRepository()
        assert hasattr(repo, 'add')


def test_cannot_access_dto_type_with_class_inheritance():
    with in_collection(SimpleDTO) as coll:
        with pytest.raises(NoDTOTypeException):
            class A(Generic[DTO]):
                ...

            @use_collection(coll)
            class B(BaseMongoRepository, A):
                ...

            _ = B()
