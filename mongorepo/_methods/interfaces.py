import typing as t

from mongorepo._base import Dataclass, SessionType

if t.TYPE_CHECKING:
    from pymongo.results import InsertManyResult, UpdateResult


class MongorepoMethod(t.Protocol[SessionType]):
    session: SessionType | None


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


class IAddBatchMethod[T: Dataclass](t.Protocol):
    def __call__(self, dto_list: list[T]) -> 'InsertManyResult':
        ...


class IAddBatchMethodAsync[T: Dataclass](t.Protocol):
    async def __call__(self, dto_list: list[T]) -> 'InsertManyResult':
        ...


class IGetAllMethod[T: Dataclass](t.Protocol):
    def __call__(self, **filters: t.Any) -> t.Generator[T, None, None]:
        ...


class IGetAllMethodAsync[T: Dataclass](t.Protocol):
    async def __call__(self, **filters: t.Any) -> t.AsyncGenerator[T, None]:
        ...


class IGetListMethod[T: Dataclass](t.Protocol):
    def __call__(self, offset: int, limit: int, **filters: t.Any) -> list[T]:
        ...


class IGetListMethodAsync[T: Dataclass](t.Protocol):
    async def __call__(self, offset: int, limit: int, **filters: t.Any) -> list[T]:
        ...


class IDeleteMethod(t.Protocol):
    def __call__(self, **filters: t.Any) -> bool:
        ...


class IDeleteMethodAsync(t.Protocol):
    async def __call__(self, **filters: t.Any) -> bool:
        ...


class IUpdateMethod[T: Dataclass](t.Protocol):
    def __call__(self, dto: T, **filters: t.Any) -> T | None:
        ...


class IUpdateMethodAsync[T: Dataclass](t.Protocol):
    async def __call__(self, dto: T, **filters: t.Any) -> T | None:
        ...


class IUpdateArrayMethod[T: Dataclass](t.Protocol):
    def __call__(self, value: t.Any, **filters: t.Any) -> 'UpdateResult':
        ...


class IUpdateArrayMethodAsync[T: Dataclass](t.Protocol):
    async def __call__(self, value: t.Any, **filters: t.Any) -> 'UpdateResult':
        ...


class IPopListMethod[T](t.Protocol):
    def __call__(self, **filters: t.Any) -> T | None:
        ...


class IPopListMethodAsync[T](t.Protocol):
    async def __call__(self, **filters: t.Any) -> T | None:
        ...


class IGetListValuesMethod[T](t.Protocol):
    def __call__(
        self, offset: int = 0, limit: int = 20, **filters: t.Any,
    ) -> list[T] | list[t.Any] | None:
        ...


class IGetListValuesMethodAsync[T](t.Protocol):
    async def __call__(
        self, offset: int = 0, limit: int = 20, **filters: t.Any,
    ) -> list[T] | list[t.Any] | None:
        ...


class IIncrementIntegerFieldMethod(t.Protocol):
    def __call__(self, weight: int | None = None, **filters) -> 'UpdateResult':
        ...


class IIncrementIntegerFieldMethodAsync(t.Protocol):
    async def __call__(self, weight: int | None = None, **filters) -> 'UpdateResult':
        ...
