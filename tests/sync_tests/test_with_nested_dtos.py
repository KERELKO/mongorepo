import pytest

from tests.common import (  # noqa
    NestedDTO,
    NestedListDTO,
    SimpleDTO,
    DTOWithDict,
    custom_collection,
)
from mongorepo.classes import BaseMongoRepository


def test_methods_with_nested_dto() -> None:
    class Repo(BaseMongoRepository[NestedDTO]):
        class Meta:
            collection = custom_collection(dto_name=NestedDTO.__name__)

    new_dto = NestedDTO(title='ho ho ho', simple=SimpleDTO(x='x', y=1))

    repo = Repo()
    repo.add(new_dto)

    dto: NestedDTO | None = repo.get(title='ho ho ho')
    assert dto is not None
    assert dto.title == 'ho ho ho'

    assert dto.simple.x == 'x'


@pytest.mark.skip
def test_methods_with_nested_list_dto() -> None:
    ...


@pytest.mark.skip
def test_methods_with_dict_dto() -> None:
    ...
