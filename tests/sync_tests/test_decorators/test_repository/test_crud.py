# mypy: disable-error-code="attr-defined"
import random

from mongorepo import repository
from mongorepo.types import MethodAccess, RepositoryConfig
from tests.common import (
    EntityWithID,
    MultiFieldEntity,
    SimpleEntity,
    in_collection,
    r,
)


def test_all_methods_with_decorator() -> None:
    with in_collection(SimpleEntity) as cl:
        @repository(config=RepositoryConfig(entity_type=SimpleEntity, collection=cl))
        class TestMongoRepository:
            ...

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


def test_can_get_dto_with_id() -> None:

    with in_collection(EntityWithID) as cl:
        @repository(RepositoryConfig(entity_type=EntityWithID, collection=cl))
        class TestMongoRepository:
            ...

        num = random.randint(1, 12346)

        repo = TestMongoRepository()
        new_dto: EntityWithID = repo.add(EntityWithID(x='entity with id', y=num))
        assert new_dto.x == 'entity with id'

        entity: EntityWithID = repo.get(y=num)
        assert entity._id is not None


def test_can_handle_complicated_dto() -> None:

    with in_collection(MultiFieldEntity) as cl:
        @repository(RepositoryConfig(entity_type=MultiFieldEntity, collection=cl))
        class TestMongoRepository:
            ...

        repo = TestMongoRepository()
        repo.add(MultiFieldEntity(x='comp', y=True, name='You', skills=['h', 'e']))

        resolved_dto = repo.get(name='You')
        assert resolved_dto.skills == ['h', 'e'] and resolved_dto.x == 'comp'


def test_can_update_partially() -> None:

    with in_collection(MultiFieldEntity) as cl:
        @repository(RepositoryConfig(entity_type=MultiFieldEntity, collection=cl))
        class TestMongoRepository:
            ...

        repo = TestMongoRepository()
        repo.add(MultiFieldEntity(x='Test', y=True, name='Me'))
        repo.update(name='Me', entity=MultiFieldEntity(x='Test', skills=['hello!'], name='Me'))

        updated_dto = repo.get(name='Me')
        assert updated_dto.skills == ['hello!']


def test_can_search_with_id() -> None:
    with in_collection(EntityWithID) as cl:
        @repository(RepositoryConfig(entity_type=EntityWithID, collection=cl))
        class TestMongoRepository:
            ...

        repo = TestMongoRepository()
        _dto = repo.add(EntityWithID(x='ID', y=10))
        assert _dto
        assert _dto._id is not None

        entity: EntityWithID = repo.get(_id=_dto._id)
        assert entity is not None
        assert entity.x == 'ID'


def test_can_make_methods_protected() -> None:

    with in_collection(SimpleEntity) as cl:
        @repository(
            RepositoryConfig(entity_type=SimpleEntity, method_access=MethodAccess.PROTECTED, collection=cl),
        )
        class TestMongoRepository:
            ...

            def access_protected_method(self) -> None:
                _ = self._get(name='Antony')  # type: ignore

        repo = TestMongoRepository()
        # check if repository has protected fields
        _ = repo._get(name='Antony')
        _ = repo._get_all()
        repo.access_protected_method()


def test_can_make_methods_private() -> None:

    with in_collection(SimpleEntity) as cl:
        @repository(
            RepositoryConfig(entity_type=SimpleEntity, collection=cl, method_access=MethodAccess.PRIVATE),
        )
        class TestMongoRepository:
            ...

            def get(self) -> bool:
                _ = self.__get(id='370r-o0-o23')  # type: ignore[attr-defined]
                return True

        repo = TestMongoRepository()

        # check if repository has private fields, this name because of the mangling
        assert hasattr(repo, f'_{TestMongoRepository.__name__}__get')

        assert repo.get() is True


def test_can_access_dto_in_type_hints_decorator() -> None:

    with in_collection(SimpleEntity) as cl:
        @repository(delete=False, config=RepositoryConfig(entity_type=SimpleEntity, collection=cl))
        class TestMongoRepository:
            ...

        repo = TestMongoRepository()

        assert hasattr(repo, 'add')
        assert not hasattr(repo, 'delete')


def test_get_list_method() -> None:

    with in_collection(SimpleEntity) as cl:
        @repository(get_list=True, config=RepositoryConfig(entity_type=SimpleEntity, collection=cl))
        class TestMongoRepository:
            ...

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


def test_get_list_with_add_batch_methods_with_decorator() -> None:

    with in_collection(SimpleEntity) as cl:
        @repository(add_batch=True, get_list=True, config=RepositoryConfig(entity_type=SimpleEntity, collection=cl))
        class TestMongoRepository:
            ...

        repo = TestMongoRepository()

        repo.add_batch(
            [SimpleEntity(x='hey', y=r()), SimpleEntity(x='second hey!', y=r())],
        )

        entity_list = repo.get_list(offset=0, limit=10)
        for entity in entity_list:
            assert entity
            assert isinstance(entity, SimpleEntity)
