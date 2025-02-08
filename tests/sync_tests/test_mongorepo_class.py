# type: ignore
import random
from typing import Generic

import pytest

from mongorepo import DTO, Index
from mongorepo.classes import BaseMongoRepository
from mongorepo.exceptions import NoDTOTypeException
from tests.common import (
    ComplicatedDTO,
    DTOWithID,
    SimpleDTO,
    collection_for_complicated_dto,
    collection_for_dto_with_id,
    collection_for_simple_dto,
)


def test_all_methods_with_inherited_repo():
    cl = collection_for_simple_dto()

    class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
        ...

    num = random.randint(1, 12346)
    unum = random.randint(1, 4567)
    repo = TestMongoRepository(cl)

    new_dto: SimpleDTO = repo.add(SimpleDTO(x='hey', y=num))
    assert new_dto.x == 'hey'

    updated_dto = repo.update(SimpleDTO(x='hey all!', y=unum), y=num)
    assert updated_dto.x == 'hey all!'

    for selected_dto in repo.get_all():
        assert selected_dto.x == 'hey all!'
        break

    dto: SimpleDTO | None = repo.get(y=unum)
    assert dto is not None

    is_deleted = repo.delete(y=unum)
    assert is_deleted is True

    dto = repo.get(y=unum)
    assert dto is None

    cl.drop()


def test_can_get_dto_with_id():
    cl = collection_for_dto_with_id()

    class TestMongoRepository(BaseMongoRepository[DTOWithID]):
        ...

    num = random.randint(1, 12346)
    repo = TestMongoRepository(cl)

    new_dto: DTOWithID = repo.add(DTOWithID(x='dto with id', y=num))
    assert new_dto.x == 'dto with id'

    dto: DTOWithID = repo.get(y=num)  # type: ignore
    assert dto._id is not None

    cl.drop()


def test_can_handle_complicated_dto():
    cl = collection_for_complicated_dto()

    class TestMongoRepository(BaseMongoRepository[ComplicatedDTO]):
        ...

    repo = TestMongoRepository(cl)

    repo.add(ComplicatedDTO(x='comp', y=True, name='You', skills=['h', 'e']))

    resolved_dto = repo.get(name='You')
    assert resolved_dto.skills == ['h', 'e'] and resolved_dto.x == 'comp'  # type: ignore

    cl.drop()


def test_can_update_partially():
    cl = collection_for_complicated_dto()

    class TestMongoRepository(BaseMongoRepository[ComplicatedDTO]):
        ...

    repo = TestMongoRepository(cl)

    repo.add(ComplicatedDTO(x='Test', y=True, name='Me'))
    repo.update(name='Me', dto=ComplicatedDTO(x='Test', skills=['hello!'], name='Me'))

    updated_dto = repo.get(name='Me')
    assert updated_dto.skills == ['hello!']  # type:ignore

    cl.drop()


def test_can_search_with_id():
    cl = collection_for_dto_with_id()

    class TestMongoRepository(BaseMongoRepository[DTOWithID]):
        ...

    repo = TestMongoRepository(cl)

    dto_id = repo.add(DTOWithID(x='ID', y=23450))._id

    dto: DTOWithID = repo.get(_id=dto_id)  # type: ignore
    assert dto.x == 'ID'

    cl.drop()


def test_can_add_index():
    cl = collection_for_simple_dto()
    _index = Index(field='y', name='y_index', desc=True, unique=False)

    class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
        class Meta:
            index = _index
            collection = cl

    repo = TestMongoRepository()

    assert 'y_index' in repo.collection.index_information()

    cl.drop()


def test_can_access_dto_type_in_type_hints_class_repo():
    cl = collection_for_simple_dto()

    class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
        ...

    _ = TestMongoRepository(cl)


def test_cannot_access_dto_type_in_type_hints_class():
    with pytest.raises(NoDTOTypeException):
        class TestMongoRepository(BaseMongoRepository):
            ...

        _ = TestMongoRepository(collection=collection_for_simple_dto())


def test_move_collection_init_to_meta_in_class_repo():
    class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
        class Meta:
            collection = collection_for_simple_dto()

    repo = TestMongoRepository()
    assert hasattr(repo, 'add')


def test_cannot_access_dto_type_with_class_inheritance():
    with pytest.raises(NoDTOTypeException):
        class A(Generic[DTO]):
            ...

        class B(BaseMongoRepository, A):
            ...

        _ = B(collection=collection_for_simple_dto())
