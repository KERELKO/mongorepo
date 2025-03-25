import typing as t
from abc import ABC, abstractmethod
from dataclasses import asdict, make_dataclass

from mongorepo._base import Dataclass

P = t.ParamSpec('P')


class ModifierBefore(t.Generic[P], ABC):
    """Abstract base class for modifying input parameters of a `mongorepo`
    method.

    Implement `modify` to transform arguments before execution.
    If no modifications are needed, return them unchanged.
    Other modifiers will use the returned values as input.

    ### NOTE:
    If modifying methods that accept filters:
    1. Filter names will be mapped to dataclass field names. Example:

        @dataclass
        class User:
            name: str

        alias = FieldAlias('name', 'username')

        # Use 'name' instead of 'username'
        def modify(self, name: str):
            ...

    2. If modifying a specific filter, return it as a dictionary:

        def modify(self, id: str) -> dict[str, str]:
            return {'id': id}

    3. If passing multiple arguments unchanged, return them as a tuple in input order:

        def modify(self, a: int, b: str, c: bool, **kwargs) -> tuple[int, str, bool, dict]:
            return (a, b, c, kwargs)

    """

    @abstractmethod
    def modify(self, *args: P.args, **kwargs: P.kwargs) -> t.Any:
        ...


class ModifierAfter[RT](ABC):
    """Abstract base class for modifying the result of a `mongorepo` method.

    Implement `modify` to transform the result before returning it.
    If no modifications are needed, return the input unchanged.
    Other modifiers will use the returned value.

    """

    @abstractmethod
    def modify(self, data: RT) -> t.Any:
        ...


class UpdateSkipModifier[T: Dataclass](ModifierBefore[T]):
    """### Modifier to skip updating dataclass fields values that equal to
    specific value.

    Apply to methods that implement `IUpdateMethod`, `IUpdateMethodAsync` protocols
    * Works with `mongorepo.impelement.methods.UpdateMethod` class

    """

    def __init__(self, skip_if_value: t.Any) -> None:
        self.skip_if_value = skip_if_value

    def modify(self, dto: T, **filters: t.Any) -> tuple[Dataclass, dict[str, t.Any]]:
        _d = asdict(dto)
        new_dataclass = make_dataclass(
            f'{self.__class__.__name__}Dataclass',
            [
                (k, 'typing.Any', f)
                for k, f in dto.__dataclass_fields__.items()
                if _d[k] != self.skip_if_value
            ],
            bases=dto.__class__.__bases__,
        )
        new_dto = new_dataclass(**{k: v for k, v in _d.items() if v != self.skip_if_value})
        return new_dto, filters


class RaiseExceptionModifier(ModifierAfter[t.Any]):
    """Raise exception when result of method execution equals to specific
    value."""
    def __init__(self, exc: Exception | type[Exception], raise_when_result: t.Any) -> None:
        self.exc = exc
        self.raise_when_result = raise_when_result

    def modify(self, data: t.Any) -> t.Any:
        if data == self.raise_when_result:
            raise self.exc
        return data
