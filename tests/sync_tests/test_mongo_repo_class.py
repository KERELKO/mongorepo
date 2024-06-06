# type: ignore
import random

from mongorepo.base import Index

from tests.common import (
    SimpleDTO,
    DTOWithID,
    ComplicatedDTO,
    collection_for_complicated_dto,
    collection_for_dto_with_id,
    collection_for_simple_dto,
)

from mongorepo.classes import BaseMongoRepository


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

    class TestMongoRepository(BaseMongoRepository[SimpleDTO]):
        ...

    index = Index(field='y', name='y_index', desc=True, unique=False)
    repo = TestMongoRepository(cl, index=index)

    assert 'y_index' in repo.collection.index_information()

    cl.drop()
