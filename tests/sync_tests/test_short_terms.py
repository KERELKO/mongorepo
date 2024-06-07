from mongorepo.decorators import mongo_repository
from mongorepo.base import Index
from tests.common import SimpleDTO, collection_for_simple_dto


def test_multiple_indexes_decorator():
    my_index = Index(field='x', name='my_index', desc=True, unique=True)

    @mongo_repository
    class A:
        class Meta:
            index = my_index
            dto = SimpleDTO
            collection = collection_for_simple_dto()

    @mongo_repository
    class B:
        class Meta:
            index = my_index
            dto = SimpleDTO
            collection = collection_for_simple_dto()

    _ = A()
    _ = B()
