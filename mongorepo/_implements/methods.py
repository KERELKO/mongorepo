import inspect
from enum import StrEnum
from typing import Callable, Literal, Protocol

from mongorepo._methods import CRUD_METHODS
from mongorepo.asyncio._methods import CRUD_METHODS_ASYNC


class ParameterEnum(StrEnum):
    FILTER = 'filters'
    OFFSET = 'offset'
    LIMIT = 'limit'
    DTO = 'dto'
    VALUE = 'value'
    WEIGHT = 'weight'


LParameter = Literal['filters', 'offset', 'limit', 'dto', 'value', 'weight']


class Method:
    def __init__(
        self,
        source: Callable,
        **params: LParameter,
    ) -> None:
        self.source: Callable = source
        self.params: dict[str, LParameter] = params
        self.name: str = source.__name__

    def __repr__(self) -> str:
        params_repr = ', '.join(f'{k}={v}' for k, v in self.params.items())
        return (
            f'Method({self.source}, {self.name}, {params_repr})'
        )

    @property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.source)

    def get_source_params(self, exclude_self: bool = True) -> dict:
        gen_params = dict(self.signature.parameters)
        if exclude_self:
            gen_params.pop('self')
        return gen_params

    @property
    def is_async(self) -> bool:
        return inspect.iscoroutinefunction(self.source)


class SpecificMethod(Protocol):
    mongorepo_method: Callable
    name: str
    source: Callable
    params: dict[str, LParameter]


class GetMethod(Method):
    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore
        self.mongorepo_method = CRUD_METHODS_ASYNC['get'] if self.is_async else CRUD_METHODS['get']


class AddMethod(Method):
    def __init__(self, source: Callable, dto: str) -> None:
        super().__init__(source, **{dto: 'dto'})  # type: ignore
        self.mongorepo_method = CRUD_METHODS_ASYNC['add'] if self.is_async else CRUD_METHODS['add']


class UpdateMethod(Method):
    def __init__(self, source: Callable, dto: str, filters: list[str]) -> None:
        super().__init__(source, dto=dto, **dict.fromkeys(filters, 'filters'))  # type: ignore


class DeleteMethod(Method):
    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore
