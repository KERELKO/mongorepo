# type: ignore
import random

import pytest

from mongorepo import Access
from mongorepo.decorators import mongo_repository
from mongorepo.exceptions import NoDTOTypeException
from tests.common import (
    MultiFieldEntity,
    EntityWithID,
    SimpleEntity,
    r,
    in_collection
)


def test_all_methods_with_decorator():
    with in_collection(SimpleEntity) as cl:
        @mongo_repository
        class TestMongoRepository:
            class Meta:
                entity = SimpleEntity
                collection = cl

        num = random.randint(1, 123456)

        repo = TestMongoRepository()
        new_dto: SimpleEntity = repo.add(SimpleEntity(x='hey', y=num))
        assert new_dto.x == 'hey'

        updated_dto = repo.update(SimpleEntity(x='hey all!', y=13), y=num)
        assert updated_dto.x == 'hey all!'

        for entity in repo.get_all():
            assert isinstance(entity, SimpleEntity)

        entity = repo.get(y=13)
        assert entity is not None

        is_deleted = repo.delete(y=13)
        assert is_deleted is True

        entity = repo.get(y=13)
        assert entity is None


def test_can_get_dto_with_id():

    with in_collection(EntityWithID) as cl:
        @mongo_repository
        class TestMongoRepository:
            class Meta:
                entity = EntityWithID
                collection = cl

        num = random.randint(1, 12346)

        repo = TestMongoRepository()
        new_dto: EntityWithID = repo.add(EntityWithID(x='entity with id', y=num))
        assert new_dto.x == 'entity with id'

        entity: EntityWithID = repo.get(y=num)
        assert entity._id is not None


def test_can_handle_complicated_dto():

    with in_collection(MultiFieldEntity) as cl:
        @mongo_repository
        class TestMongoRepository:
            class Meta:
                entity = MultiFieldEntity
                collection = cl

        repo = TestMongoRepository()
        repo.add(MultiFieldEntity(x='comp', y=True, name='You', skills=['h', 'e']))

        resolved_dto = repo.get(name='You')
        assert resolved_dto.skills == ['h', 'e'] and resolved_dto.x == 'comp'


def test_can_update_partially():

    with in_collection(MultiFieldEntity) as cl:
        @mongo_repository
        class TestMongoRepository:
            class Meta:
                entity = MultiFieldEntity
                collection = cl

        repo = TestMongoRepository()
        repo.add(MultiFieldEntity(x='Test', y=True, name='Me'))
        repo.update(name='Me', entity=MultiFieldEntity(x='Test', skills=['hello!'], name='Me'))

        updated_dto = repo.get(name='Me')
        assert updated_dto.skills == ['hello!']


def test_can_search_with_id():
    with in_collection(EntityWithID) as cl:
        @mongo_repository
        class TestMongoRepository:
            class Meta:
                entity = EntityWithID
                collection = cl

        repo = TestMongoRepository()
        _dto = repo.add(EntityWithID(x='ID', y=10))
        assert _dto
        assert _dto._id is not None

        entity: EntityWithID = repo.get(_id=_dto._id)
        assert entity is not None
        assert entity.x == 'ID'


def test_can_make_methods_protected():

    with in_collection(SimpleEntity) as cl:
        @mongo_repository
        class TestMongoRepository:
            class Meta:
                entity = SimpleEntity
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

    with in_collection(SimpleEntity) as cl:
        @mongo_repository
        class TestMongoRepository:
            class Meta:
                entity = SimpleEntity
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

    with in_collection(SimpleEntity) as cl:
        @mongo_repository(delete=False)
        class TestMongoRepository:
            class Meta:
                entity = SimpleEntity
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

    with in_collection(SimpleEntity) as cl:
        @mongo_repository(get_list=True)
        class TestMongoRepository:
            class Meta:
                entity = SimpleEntity
                collection = cl

        r = TestMongoRepository()
        r.add(SimpleEntity(x='123', y=123))
        r.add(SimpleEntity(x='234', y=999))

        dtos = r.get_list(offset=0, limit=2)
        assert len(dtos) == 2

        dtos = r.get_list(offset=1, limit=2)

        assert len(dtos) == 1
        assert dtos[0].x == '234'

        dtos = r.get_list(offset=0, limit=1)

        assert len(dtos) == 1
        assert dtos[0].x == '123'


def test_get_list_with_add_batch_methods_with_decorator():

    with in_collection(SimpleEntity) as cl:
        @mongo_repository(add_batch=True, get_list=True)
        class TestMongoRepository:
            class Meta:
                entity = SimpleEntity
                collection = cl

        repo = TestMongoRepository()

        repo.add_batch(
            [SimpleEntity(x='hey', y=r()), SimpleEntity(x='second hey!', y=r())],
        )

        dto_list = repo.get_list(offset=0, limit=10)
        for entity in dto_list:
            assert entity
            assert isinstance(entity, SimpleEntity)
