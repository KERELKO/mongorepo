import functools
from dataclasses import dataclass, field

from mongorepo.utils.entity_converters import (
    _nested_convert_to_dto,
    get_converter,
)


def test_nested_converts_to_dto() -> None:
    @dataclass
    class SimpleEntity:
        x: str
        y: int

    @dataclass
    class NestedEntity:
        title: str
        simple: SimpleEntity

    @dataclass
    class NestedListEntity:
        title: str = 'Nested Entity'
        dtos: list[SimpleEntity] = field(default_factory=list)

    @dataclass
    class VeryNestedDTO:
        dtos: list[NestedListEntity]

    simple_dto = SimpleEntity(x='123', y=5)
    assert _nested_convert_to_dto(SimpleEntity, {'x': '123', 'y': 5}) == simple_dto

    nested_dto = NestedEntity(title='.', simple=simple_dto)
    assert _nested_convert_to_dto(
        NestedEntity, {'title': '.', 'simple': {'x': '123', 'y': 5}},
    ) == nested_dto
    nested_list_dto = NestedListEntity(title='...', dtos=[simple_dto, simple_dto, simple_dto])
    convert = _nested_convert_to_dto(
        NestedListEntity,
        data={
            'title': '...', 'dtos': [
                {'x': '123', 'y': 5}, {'x': '123', 'y': 5}, {'x': '123', 'y': 5},
            ],
        },
    )
    assert convert == nested_list_dto, convert

    recursive_dto = VeryNestedDTO(
        dtos=[nested_list_dto, nested_list_dto],
    )
    final_conv = _nested_convert_to_dto(
        VeryNestedDTO,
        data={
            'dtos': [
                {
                    'title': '...', 'dtos': [
                        {'x': '123', 'y': 5}, {'x': '123', 'y': 5}, {'x': '123', 'y': 5},
                    ],
                },
                {
                    'title': '...', 'dtos': [
                        {'x': '123', 'y': 5}, {'x': '123', 'y': 5}, {'x': '123', 'y': 5},
                    ],
                },
            ],
        },
    )

    assert recursive_dto == final_conv, final_conv


@dataclass
class User:
    id: str
    username: str
    friends: list['User'] = field(default_factory=list)


to_user = functools.partial(get_converter(User), User)

dct = {
    'id': '1',
    'username': 'admin',
    'friends': [
        {'id': 2, 'username': 'bob', 'friends': []},
        {
            'id': 3, 'username': 'destroyer', 'friends': [
                {'id': 4, 'username': 'top_1', 'friends': []},
            ],
        },
    ],
}
user = to_user(dct)

assert user.friends[1].friends[0].id == 4
