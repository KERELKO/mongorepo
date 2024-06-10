from abc import ABC
from typing import Generic

from mongorepo.base import DTO
from mongorepo.decorators import substitute
from tests.common import ComplicatedDTO, collection_for_complicated_dto


def test_can_substitute_methods_with_decorator():
    # Idea: to dynamically replace methods of mongo repo class with other class methods

    class BaseRepository(Generic[DTO], ABC):
        def get_by_name(self, name: str) -> DTO | None:
            raise NotImplementedError

        def create(self, entity: DTO) -> DTO:
            raise NotImplementedError

    @substitute(BaseRepository)
    class SubstitudeWithDecorator(BaseRepository[ComplicatedDTO]):
        class Meta:
            dto = ComplicatedDTO
            substitute = {'get': 'get_by_name', 'add': 'create'}
            collection = collection_for_complicated_dto()

    repo_dec = SubstitudeWithDecorator()

    assert hasattr(repo_dec, 'create')
    assert hasattr(repo_dec, 'get_by_name')
    dto = ComplicatedDTO(x='test', name='admin', y=True, skills=['python'])
    repo_dec.create(entity=dto)

    record: ComplicatedDTO | None = repo_dec.get_by_name(name='admin')  # type: ignore
    assert record is not None
    assert record.name == 'admin'
    assert record.y is True
    assert record.skills == ['python']
