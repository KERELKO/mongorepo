from bson import ObjectId
from .conftest import SimpleDTO, DTOWithID, ComplicatedDTO

from conf import mongo_client
from mongorepo.decorators import mongo_repository_factory


def test_all_methods_with_decorator():

    @mongo_repository_factory
    class TestMongoRepository:
        class Meta:
            dto = SimpleDTO
            collection = mongo_client()['simple_dto_db']['dto']

    repo = TestMongoRepository()
    new_dto: SimpleDTO = repo.create(SimpleDTO(x='hey', y=1))
    assert new_dto.x == 'hey'

    updated_dto = repo.update(SimpleDTO(x='hey all!', y=1), y=1)
    assert updated_dto.x == 'hey all!'

    for dto in repo.get_all():
        assert dto.x == 'hey all!'
        break

    dto = repo.get(y=1)
    assert dto is not None

    is_deleted = repo.delete(y=1)
    assert is_deleted is True

    dto = repo.get(y=1)
    assert dto is None


def test_can_get_dto_with_id():

    @mongo_repository_factory
    class TestMongoRepository:
        class Meta:
            dto = DTOWithID
            collection = mongo_client()['dto_with_id_db']['dto']

    repo = TestMongoRepository()
    new_dto: DTOWithID = repo.create(DTOWithID(x='dto with id', y=1))
    assert new_dto.x == 'dto with id'

    dto: DTOWithID = repo.get(y=1)
    assert dto._id is not None

    assert isinstance(dto._id, ObjectId)


def test_can_handle_complicated_dto():

    @mongo_repository_factory
    class TestMongoRepository:
        class Meta:
            dto = ComplicatedDTO
            collection = mongo_client()['dto_complicated']['dto']

    repo = TestMongoRepository()
    repo.create(ComplicatedDTO(x='comp', y=True, name='You', skills=['h', 'e']))

    resolved_dto = repo.get(name='You')
    assert resolved_dto.skills == ['h', 'e'] and resolved_dto.x == 'comp'


def test_can_update_partially():

    @mongo_repository_factory
    class TestMongoRepository:
        class Meta:
            dto = ComplicatedDTO
            collection = mongo_client()['dto_complicated']['dto']

    repo = TestMongoRepository()
    repo.create(ComplicatedDTO(x='Test', y=True, name='Me'))
    repo.update(ComplicatedDTO(x='Test', skills=['hello!'], name='Me'), name='Me')

    updated_dto = repo.get(name='Me')
    assert updated_dto.skills == ['hello!']


def test_can_search_with_id():

    @mongo_repository_factory
    class TestMongoRepository:
        class Meta:
            dto = DTOWithID
            collection = mongo_client()['dto_with_id_db']['dto']

    repo = TestMongoRepository()
    dto_id: DTOWithID = repo.create(DTOWithID(x='ID', y=10))._id

    dto: DTOWithID = repo.get(_id=dto_id)
    assert dto.x == 'ID'

    assert isinstance(dto._id, ObjectId)
