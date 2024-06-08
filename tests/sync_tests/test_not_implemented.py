# type: ignore
from typing import Generic

import pytest

from mongorepo.base import DTO

from tests.common import ComplicatedDTO, collection_for_complicated_dto


@pytest.mark.skip(reason='Not implemented yet')
def test_can_replace_methods_with_parent_class_methods():
    # Idea: to dynamically replace methods of mongo repo class with parent class methods

    class MongoSubstitutionRepository:
        ...

    class BaseRepository(Generic[DTO]):
        def get_by_x(self, x: str) -> DTO | None:
            ...

    @mongo_repository_substitute  # noqa
    class MongoRepository(
        MongoSubstitutionRepository[ComplicatedDTO],
        BaseRepository[ComplicatedDTO]
    ):
        class Meta:
            substitute = {'get': 'get_by_x'}

    repo = MongoRepository(collection_for_complicated_dto())

    _ = repo.get_by_x(x='23')
