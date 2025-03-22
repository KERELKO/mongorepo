import typing as t
from abc import ABC, abstractmethod

from mongorepo._base import Dataclass

P = t.ParamSpec('P')


class ModifierBefore(t.Generic[P], ABC):
    """Abstract modifier class that modifies input parameters of mongorepo
    method."""

    @abstractmethod
    def modify(self, *args: P.args, **kwargs: P.kwargs) -> None:
        ...


class ModifierAfter[RT](ABC):
    """Abstract modifier class that modifies mongorepo method result."""

    @abstractmethod
    def modify(self, data: RT) -> None:
        ...


class UpdateSkipModifier[T: Dataclass](ModifierBefore[T]):
    def __init__(self, skip_if_value: t.Any) -> None:
        self.skip_if_value = skip_if_value

    def modify(self, dto: T, **filters: t.Any) -> None:
        ...


class ModifierException(ModifierAfter[t.Any]):
    def __init__(self, exc: Exception, raise_when_result: t.Any) -> None:
        self.exc = exc
        self.raise_when_result = raise_when_result

    def modify(self, data: t.Any) -> None:
        if data == self.raise_when_result:
            raise self.exc
