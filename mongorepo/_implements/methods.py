import inspect
from enum import StrEnum
from typing import Callable, Literal


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


class GetMethod(Method):
    def __init__(self, source: Callable, filters: tuple[str, ...]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore


class AddMethod(Method):
    def __init__(self, source: Callable, dto: str) -> None:
        super().__init__(source, **{dto: 'dto'})  # type: ignore
