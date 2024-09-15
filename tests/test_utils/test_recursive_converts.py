from dataclasses import dataclass, field

from mongorepo.utils import _recursive_convert_to_dto


def test_recursive_converts_to_dto() -> None:
    @dataclass
    class SimpleDTO:
        x: str
        y: int

    @dataclass
    class NestedDTO:
        title: str
        simple: SimpleDTO

    @dataclass
    class NestedListDTO:
        title: str = 'Nested DTO'
        dtos: list[SimpleDTO] = field(default_factory=list)

    @dataclass
    class RecursiveDTO:
        dtos: list[NestedListDTO]

    s = SimpleDTO(x='123', y=5)
    assert _recursive_convert_to_dto(SimpleDTO)(SimpleDTO, {'x': '123', 'y': 5}) == s

    n = NestedDTO(title='.', simple=s)
    assert _recursive_convert_to_dto(NestedDTO)(
        NestedDTO, {'title': '.', 'simple': {'x': '123', 'y': 5}}
    ) == n
    nl = NestedListDTO(title='...', dtos=[s, s, s])
    conv = _recursive_convert_to_dto(NestedListDTO)(
        NestedListDTO,
        dct={
            'title': '...', 'dtos': [
                {'x': '123', 'y': 5}, {'x': '123', 'y': 5}, {'x': '123', 'y': 5}
            ]
        }
    )
    assert conv == nl, conv

    rnl = RecursiveDTO(
        dtos=[nl, nl]
    )
    final_conv = _recursive_convert_to_dto(RecursiveDTO)(
        RecursiveDTO,
        dct={
            'dtos': [
                {'title': '...', 'dtos': [
                    {'x': '123', 'y': 5}, {'x': '123', 'y': 5}, {'x': '123', 'y': 5}
                ]},
                {'title': '...', 'dtos': [
                    {'x': '123', 'y': 5}, {'x': '123', 'y': 5}, {'x': '123', 'y': 5}
                ]},
            ]
        }
    )

    assert rnl == final_conv, final_conv
