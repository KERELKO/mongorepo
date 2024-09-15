# type: ignore
import random

import pytest

from mongorepo import Access
from tests.common import (
    SimpleDTO,
    DTOWithID,
    ComplicatedDTO,
    collection_for_complicated_dto,
    collection_for_dto_with_id,
    collection_for_simple_dto,
    r,
)

from mongorepo.exceptions import NoDTOTypeException
from mongorepo.decorators import mongo_repository


def test_all_methods_with_decorator():
    cl = collection_for_simple_dto()

    @mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl

    num = random.randint(1, 123456)

    repo = TestMongoRepository()
    new_dto: SimpleDTO = repo.add(SimpleDTO(x='hey', y=num))
    assert new_dto.x == 'hey'

    updated_dto = repo.update(SimpleDTO(x='hey all!', y=13), y=num)
    assert updated_dto.x == 'hey all!'

    for dto in repo.get_all():
        assert isinstance(dto, SimpleDTO)

    dto = repo.get(y=13)
    assert dto is not None

    is_deleted = repo.delete(y=13)
    assert is_deleted is True

    dto = repo.get(y=13)
    assert dto is None

    cl.drop()


def test_can_get_dto_with_id():
    cl = collection_for_dto_with_id()

    @mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = DTOWithID
            collection = cl

    num = random.randint(1, 12346)

    repo = TestMongoRepository()
    new_dto: DTOWithID = repo.add(DTOWithID(x='dto with id', y=num))
    assert new_dto.x == 'dto with id'

    dto: DTOWithID = repo.get(y=num)
    assert dto._id is not None

    cl.drop()


def test_can_handle_complicated_dto():
    cl = collection_for_complicated_dto()

    @mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = ComplicatedDTO
            collection = cl

    repo = TestMongoRepository()
    repo.add(ComplicatedDTO(x='comp', y=True, name='You', skills=['h', 'e']))

    resolved_dto = repo.get(name='You')
    assert resolved_dto.skills == ['h', 'e'] and resolved_dto.x == 'comp'

    cl.drop()


def test_can_update_partially():
    cl = collection_for_complicated_dto()

    @mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = ComplicatedDTO
            collection = cl

    repo = TestMongoRepository()
    repo.add(ComplicatedDTO(x='Test', y=True, name='Me'))
    repo.update(name='Me', dto=ComplicatedDTO(x='Test', skills=['hello!'], name='Me'))

    updated_dto = repo.get(name='Me')
    assert updated_dto.skills == ['hello!']

    cl.drop()


def test_can_search_with_id():
    cl = collection_for_dto_with_id()

    @mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = DTOWithID
            collection = cl

    repo = TestMongoRepository()
    _dto = repo.add(DTOWithID(x='ID', y=10))
    assert _dto
    assert _dto._id is not None

    dto: DTOWithID = repo.get(_id=_dto._id)
    assert dto is not None
    assert dto.x == 'ID'

    cl.drop()


def test_can_make_methods_protected():
    cl = collection_for_simple_dto()

    @mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl
            method_access = Access.PROTECTED

        def access_protected_method(self):
            _ = self._get(name='Antony')  # type: ignore

    repo = TestMongoRepository()
    # check if repository has protected fields
    _ = repo._get(name='Antony')
    _ = repo._get_all()
    repo.access_protected_method()


def test_can_make_methods_private():
    cl = collection_for_simple_dto()

    @mongo_repository
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl
            method_access = Access.PRIVATE

        def get(self) -> bool:
            _ = self.__get(id='370r-o0-o23')  # type: ignore
            return True

    repo = TestMongoRepository()

    # check if repository has private fields, this name because of the mangling
    assert hasattr(repo, f'_{TestMongoRepository.__name__}__get')

    assert repo.get() is True


def test_can_access_dto_in_type_hints_decorator():
    cl = collection_for_simple_dto()

    @mongo_repository(delete=False)
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl

    repo = TestMongoRepository()

    assert hasattr(repo, 'add')
    assert not hasattr(repo, 'delete')


def test_cannot_access_dto_type_in_type_hints_decorator():
    with pytest.raises(NoDTOTypeException):

        @mongo_repository
        class TestMongoRepository:
            class Meta:
                ...


def test_get_list_method():
    cl = collection_for_simple_dto()

    @mongo_repository(get_list=True)
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl

    r = TestMongoRepository()
    r.add(SimpleDTO(x='123', y=123))
    r.add(SimpleDTO(x='234', y=999))

    dtos = r.get_list(offset=0, limit=2)
    assert len(dtos) == 2

    dtos = r.get_list(offset=1, limit=2)

    assert len(dtos) == 1
    assert dtos[0].x == '234'

    dtos = r.get_list(offset=0, limit=1)

    assert len(dtos) == 1
    assert dtos[0].x == '123'

    cl.drop()


def test_get_list_with_add_batch_methods_with_decorator():
    cl = collection_for_simple_dto()

    @mongo_repository(add_batch=True, get_list=True)
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = cl

    repo = TestMongoRepository()

    repo.add_batch(
        [SimpleDTO(x='hey', y=r()), SimpleDTO(x='second hey!', y=r())]
    )

    dto_list = repo.get_list(offset=0, limit=10)
    for dto in dto_list:
        assert dto
        assert isinstance(dto, SimpleDTO)

    cl.drop()
