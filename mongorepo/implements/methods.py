import inspect
from typing import Callable, Protocol

from mongorepo._base import LParameter, MethodAction
from mongorepo._methods import CRUD_METHODS, INTEGER_METHODS, LIST_METHODS
from mongorepo.asyncio._methods import (
    CRUD_METHODS_ASYNC,
    INTEGER_METHODS_ASYNC,
    LIST_METHODS_ASYNC,
)


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
    action: MethodAction


class GetMethod(Method):
    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore
        self.action = MethodAction.GET
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class AddMethod(Method):
    def __init__(self, source: Callable, dto: str) -> None:
        super().__init__(source, **{dto: 'dto'})  # type: ignore
        self.action = MethodAction.ADD
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class UpdateMethod(Method):
    def __init__(self, source: Callable, dto: str, filters: list[str]) -> None:
        super().__init__(
            source, **{dto: 'dto'}, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.UPDATE
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class DeleteMethod(Method):
    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore
        self.action = MethodAction.DELETE
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class GetListMethod(Method):
    def __init__(self, source: Callable, offset: str, limit: str, filters: list[str]) -> None:
        super().__init__(
            source, **{offset: 'offset', limit: 'limit'},  # type: ignore
            **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.GET_LIST
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class GetAllMethod(Method):
    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore
        self.action = MethodAction.GET_ALL
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class AddBatchMethod(Method):
    def __init__(self, source: Callable, dto_list: str) -> None:
        super().__init__(source, **{dto_list: 'dto_list'})  # type: ignore
        self.action = MethodAction.ADD_BATCH
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class ListAppendMethod(Method):
    def __init__(self, source: Callable, value: str, filters: list[str]) -> None:
        super().__init__(
            source, **{value: 'value'}, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.LIST_APPEND
        self.mongorepo_method = (
            LIST_METHODS_ASYNC[self.action] if self.is_async else LIST_METHODS[self.action]
        )


class ListPopMethod(Method):
    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(
            source, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.LIST_POP
        self.mongorepo_method = (
            LIST_METHODS_ASYNC[self.action] if self.is_async else LIST_METHODS[self.action]
        )


class ListRemoveMethod(Method):
    def __init__(self, source: Callable, value: str, filters: list[str]) -> None:
        super().__init__(
            source, **{value: 'value'}, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.LIST_REMOVE
        self.mongorepo_method = (
            LIST_METHODS_ASYNC[self.action] if self.is_async else LIST_METHODS[self.action]
        )


class ListGetFieldValuesMethod(Method):
    def __init__(self, source: Callable, offset: str, limit: str, filters: list[str]) -> None:
        super().__init__(
            source, **{offset: 'offset', limit: 'limit'},  # type: ignore
            **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.LIST_FIELD_VALUES
        self.mongorepo_method = (
            LIST_METHODS_ASYNC[self.action] if self.is_async else LIST_METHODS[self.action]
        )


class IncrementIntegerFieldMethod(Method):
    def __init__(self, source: Callable, filters: list[str], weight: str | None = None) -> None:
        super().__init__(
            source, **{weight: 'weight'}, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.INTEGER_INCREMENT
        self.mongorepo_method = (
            INTEGER_METHODS_ASYNC[self.action] if self.is_async else INTEGER_METHODS[self.action]
        )


class DecrementIntergerFieldMethod(Method):
    def __init__(self, source: Callable, filters: list[str], weight: str | None = None) -> None:
        super().__init__(
            source, **{weight: 'weight'}, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.INTEGER_DECREMENT
        self.mongorepo_method = (
            INTEGER_METHODS_ASYNC[self.action] if self.is_async else INTEGER_METHODS[self.action]
        )
