from dataclasses import dataclass, field

from mongorepo.utils.dataclass_converters import (
    _nested_convert_to_dataclass,
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
    assert _nested_convert_to_dataclass({'x': '123', 'y': 5}, SimpleEntity) == simple_dto

    nested_dto = NestedEntity(title='.', simple=simple_dto)
    assert _nested_convert_to_dataclass(
        {'title': '.', 'simple': {'x': '123', 'y': 5}},
        NestedEntity,
    ) == nested_dto
    nested_list_dto = NestedListEntity(title='...', dtos=[simple_dto, simple_dto, simple_dto])
    convert = _nested_convert_to_dataclass(
        {
            'title': '...', 'dtos': [
                {'x': '123', 'y': 5}, {'x': '123', 'y': 5}, {'x': '123', 'y': 5},
            ],
        },
        NestedListEntity,
    )
    assert convert == nested_list_dto, convert

    recursive_dto = VeryNestedDTO(
        dtos=[nested_list_dto, nested_list_dto],
    )
    final_conv = _nested_convert_to_dataclass(
        {
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
        VeryNestedDTO,
    )

    assert recursive_dto == final_conv, final_conv


@dataclass
class User:
    id: str
    username: str
    friends: list['User'] = field(default_factory=list)


convert = get_converter(User)

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
user = convert(dct, User)

assert user.friends[1].friends[0].id == 4
