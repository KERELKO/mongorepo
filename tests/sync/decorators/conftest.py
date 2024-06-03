from dataclasses import dataclass, field

import pytest
from bson import ObjectId

from conf import mongo_client


@dataclass
class SimpleDTO:
    x: str
    y: int


@dataclass
class DTOWithID:
    _id: ObjectId = field(default_factory=ObjectId, kw_only=True)
    x: str
    y: int


@dataclass
class ComplicatedDTO:
    x: str
    y: bool = False
    name: str = 'Hello World!'
    skills: list[str] = field(default_factory=list)


@pytest.fixture
def simple_dto() -> SimpleDTO:
    return SimpleDTO(x='lala', y=123)


@pytest.fixture
def dto_with_id() -> DTOWithID:
    return DTOWithID(x='dto with id', y=9)


@pytest.fixture
def complicated_dto() -> ComplicatedDTO:
    return ComplicatedDTO(x='ok', name='yo', skills=['a' 'b', 'c'])
