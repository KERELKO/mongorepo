from dataclasses import dataclass, field

from mongorepo.utils import get_dataclass_type_hints, get_first_arg
from tests.common import NestedDTO, SimpleDTO


def test_can_get_nested_dto_type_hints() -> None:
    type_hints = get_dataclass_type_hints(NestedDTO)

    assert 'title' in type_hints
    assert 'simple' in type_hints
    assert type_hints['title'] is str
    assert type_hints['simple'] is SimpleDTO


def different_cases_of_type_hints():
    @dataclass
    class Profile:
        first_name: str
        avatar: str

    @dataclass
    class Message:
        id: str
        body: str

    @dataclass
    class User:
        id: str
        username: str
        profile: Profile
        other: list[str | int]
        age: int | None = None
        friends: list['User'] = field(default_factory=list)
        messages: list[Message | None] = field(default_factory=list)

    type_hints = get_dataclass_type_hints(User)
    assert type_hints['id'] is str
    assert type_hints['profile'] is Profile
    assert type_hints['other'] is list
    assert type_hints['age'] is int
    assert type_hints['friends'] is list
    assert type_hints['messages'] is list


def test_can_identify_type_hint():
    @dataclass
    class User:
        ...

    l_1 = list[list[str | int]]
    l_2 = list[int | bool]
    l_3 = list['User']

    assert get_first_arg(l_1) is list
    assert get_first_arg(l_2) is int
    assert get_first_arg(l_3) == 'User'
