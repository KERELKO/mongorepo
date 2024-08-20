import random
from dataclasses import dataclass, field

from mongorepo.utils import _get_converter


def test_can_convert_simple_parent_variables() -> None:

    @dataclass
    class BaseDTO:
        id: int = field(default_factory=lambda: random.randint(1, 200), kw_only=True)

    @dataclass
    class UserDTO(BaseDTO):
        name: str

    to_dto = _get_converter(UserDTO)

    dto: UserDTO = to_dto(UserDTO, {'_id': '-', 'name': 'Artorias', 'id': 100})

    assert dto.name == 'Artorias'
    assert dto.id == 100


def test_can_convert_simple_parent_variables_with_id_field() -> None:

    @dataclass
    class BaseDTO:
        id: int = field(default_factory=lambda: random.randint(1, 200), kw_only=True)

    @dataclass
    class UserDTO(BaseDTO):
        name: str

    to_dto = _get_converter(UserDTO, id_field='id')

    dto: UserDTO = to_dto(UserDTO, {'_id': 'id_field', 'name': 'Artorias'})

    assert dto.name == 'Artorias'
    assert dto.id == 'id_field'


def test_can_convert_simple_parent_variables_with_recursion() -> None:

    @dataclass
    class Record:
        text: str

    @dataclass
    class BaseDTO:
        id: int = field(default_factory=lambda: random.randint(1, 200), kw_only=True)

    @dataclass
    class UserDTOWithRecord(BaseDTO):
        name: str
        record: Record

    @dataclass
    class UserDTOWithListOfRecords(BaseDTO):
        name: str
        records: list[Record]

    to_dto = _get_converter(UserDTOWithRecord)

    dto: UserDTOWithRecord = to_dto(
        UserDTOWithRecord, {'id': 100, 'name': 'Artorias', 'record': {'text': 'Hello World'}}
    )

    assert dto.name == 'Artorias'
    assert dto.id == 100
    assert isinstance(dto.record, Record)
    assert dto.record.text == 'Hello World'

    to_dto_r = _get_converter(UserDTOWithListOfRecords)

    dto_r: UserDTOWithListOfRecords = to_dto_r(
        UserDTOWithListOfRecords, {'id': 101, 'name': 'admin', 'records': [{'text': 'SUCCESS'}]}
    )

    assert dto_r.id == 101
    assert dto_r.name == 'admin'
    assert isinstance(dto_r.records, list)
    assert dto_r.records[0].text == 'SUCCESS'
