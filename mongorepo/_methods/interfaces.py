import typing as t

from mongorepo._base import Dataclass


class IGetMethod[T: Dataclass](t.Protocol):
    def __call__(self, **filters: t.Any) -> T | None:
        ...


class IGetMethodAsync[T: Dataclass](t.Protocol):
    async def __call__(self, **filters: t.Any) -> T | None:
        ...


class IAddMethod[T: Dataclass](t.Protocol):
    def __call__(self, dto: T) -> T:
        ...


class IAddMethodAsync[T: Dataclass](t.Protocol):
    async def __call__(self, dto: T) -> T:
        ...


class IUpdateMethod[T: Dataclass](t.Protocol):
    async def __call__(self, dto: T, **filters: t.Any) -> T | None:
        ...


class IUpdateMethodAsync[T: Dataclass](t.Protocol):
    async def __call__(self, dto: T, **filters: t.Any) -> T | None:
        ...
