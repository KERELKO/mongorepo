from dataclasses import dataclass
from typing import Protocol, cast

import pytest

from mongorepo.exceptions import MongorepoException
from mongorepo.implement import AddMethod, GetMethod, implement
from mongorepo.implement.exceptions import FieldDoesNotExist
from mongorepo.implement.methods import FieldAlias
from tests.common import in_collection


def test_can_identify_incorrect_named_field():
    @dataclass
    class Car:
        model: str
        year: int
        engine: str

    class Repo(Protocol):
        def get(self, model: str, year: int) -> Car | None:
            ...

    with in_collection(Car) as c:
        with pytest.raises(FieldDoesNotExist):
            @implement(GetMethod(Repo.get, filters=['model', 'years']))
            class MongoRepo:
                class Meta:
                    collection = c
                    dto = Car

            repo = cast(Repo, MongoRepo())

            repo.get(model='a', year=2016)


def test_can_identify_incorrect_named_field_with_alias():
    @dataclass
    class Car:
        model: str
        year: int
        engine: str

    class Repo(Protocol):
        def add(self, car: Car):
            ...

        def get_valid(self, __model__: str, year: int) -> Car | None:
            ...

        def get_invalid(self, model: str, year: int) -> Car | None:
            ...

    with in_collection(Car) as c:
        with pytest.raises(MongorepoException):
            @implement(
                AddMethod(Repo.add, dto='car'),
                GetMethod(Repo.get_valid, filters=[FieldAlias('model', '__model__'), 'year']),
                GetMethod(Repo.get_invalid, filters=[FieldAlias('years', 'la'), 'year_INVALID']),
            )
            class MongoRepo:
                class Meta:
                    collection = c
                    dto = Car

            repo = cast(Repo, MongoRepo())

            test_car = Car(model='1', year=2014, engine='JDF-34')

            repo.add(test_car)

            repo.get_valid(__model__='1', year=2014)

            repo.get_invalid(model='1', year=2015)
