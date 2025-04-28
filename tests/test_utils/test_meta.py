from typing import cast

import mongorepo
from mongorepo.implement import implement
from mongorepo.implement.methods import AddMethod, GetMethod
from mongorepo.utils import set_meta_attrs
from tests.common import ComplicatedDTO, SimpleDTO, in_collection


def test_set_meta_attrs_decorator_with_repository():
    with in_collection(SimpleDTO) as coll:
        @mongorepo.repository
        @mongorepo.use_collection(coll)
        @set_meta_attrs(dto_type=SimpleDTO)
        class Repository:
            ...

        repo = Repository()
        repo.add(SimpleDTO(x='1', y=1))

        get_dto: SimpleDTO | None = repo.get(x='1')

        assert get_dto is not None
        assert get_dto.x == '1'


def test_set_meta_attrs_decorator_with_implement():
    with in_collection(SimpleDTO) as coll:
        class IRepo:
            def get(self, x: str) -> SimpleDTO | None:
                ...

            def add(self, simple: SimpleDTO):
                ...

        @implement(AddMethod(IRepo.add, dto='simple'), GetMethod(IRepo.get, filters=['x']))
        @mongorepo.set_meta_attrs(dto_type=SimpleDTO)
        @mongorepo.use_collection(coll)
        class MongoRepo:
            ...

        repo = cast(IRepo, MongoRepo())
        dto = SimpleDTO(x='1', y=1)
        repo.add(dto)
        get_dto = repo.get(x='1')

        assert get_dto is not None
        assert get_dto.x == '1'


def test_set_meta_attrs_decorator_with_base_repo_class():
    with in_collection(SimpleDTO) as coll:
        @mongorepo.set_meta_attrs(
            id_field='x', index='x', dto_type=ComplicatedDTO, collection=coll,
        )
        class MongoRepository(mongorepo.BaseMongoRepository):
            ...

        repo = MongoRepository()

        dto = ComplicatedDTO(x='1', y=True, name='comp', skills=['a', 'b', 'c'])

        dto_id = repo.add(dto).x

        get_dto = repo.get(x=dto_id)

        assert get_dto is not None
        assert get_dto.skills == dto.skills
