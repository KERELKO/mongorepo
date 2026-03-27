from typing import cast

import mongorepo
from mongorepo.implement import implement
from mongorepo.implement.methods import AddMethod, GetMethod
from mongorepo.utils import set_meta_attrs
from tests.common import SimpleEntity, in_collection


def test_set_meta_attrs_decorator_with_repository():
    with in_collection(SimpleEntity) as coll:
        @mongorepo.repository
        @mongorepo.use_collection(coll)
        @set_meta_attrs(entity_type=SimpleEntity)
        class Repository:
            class Meta:
                collection = coll
                entity = SimpleEntity

        repo = Repository()
        repo.add(SimpleEntity(x='1', y=1))

        get_dto: SimpleEntity | None = repo.get(x='1')

        assert get_dto is not None
        assert get_dto.x == '1'


def test_set_meta_attrs_decorator_with_implement():
    with in_collection(SimpleEntity) as coll:
        class IRepo:
            def get(self, x: str) -> SimpleEntity | None:
                ...

            def add(self, simple: SimpleEntity):
                ...

        @implement(AddMethod(IRepo.add, entity='simple'), GetMethod(IRepo.get, filters=['x']))
        @mongorepo.set_meta_attrs(entity_type=SimpleEntity)
        @mongorepo.use_collection(coll)
        class MongoRepo:
            ...

        repo = cast(IRepo, MongoRepo())
        entity = SimpleEntity(x='1', y=1)
        repo.add(entity)
        get_dto = repo.get(x='1')

        assert get_dto is not None
        assert get_dto.x == '1'
