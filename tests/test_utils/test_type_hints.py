from mongorepo.utils import _get_dto_type_hints
from tests.common import NestedDTO, SimpleDTO


def test_can_get_nested_dto_type_hints() -> None:
    type_hints = _get_dto_type_hints(NestedDTO)

    assert 'title' in type_hints
    assert 'simple' in type_hints
    assert type_hints['title'] is str
    assert type_hints['simple'] is SimpleDTO


def test_can_get_nested_list_dto_type_hints() -> None:
    type_hints = _get_dto_type_hints(NestedDTO)

    assert 'title' in type_hints
    assert 'simple' in type_hints
    assert type_hints['title'] is str
    assert type_hints['simple'] is SimpleDTO
