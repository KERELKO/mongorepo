import inspect
from dataclasses import Field, dataclass
from enum import Enum
from typing import Any, Callable, ClassVar, Protocol, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DTO = TypeVar('DTO', bound=DataclassInstance)
_DTOField = TypeVar('_DTOField', bound=DataclassInstance)


@dataclass(repr=False, slots=True, eq=False)
class Index:
    """Allows to specify extra information about mongodb index."""
    field: str
    name: str | None = None
    desc: bool = True
    unique: bool = False


class Access(int, Enum):
    """Use to indicate method access in a repository."""
    PUBLIC = 0
    PROTECTED = 1
    PRIVATE = 2


class _FiltersParameter(str, Enum):
    FILTER = 'filters'


@dataclass(eq=False)
class _MethodDeps:
    """DTO for mongorepo methods dependencies.

    ### includes:
    ```
    collection: Collection | AsyncIOMotorCollection | None = None
    dto: type[DTO] | None = None
    id_field: str | None = None
    field_name: str | None = None
    ```

    """
    collection: Collection | AsyncIOMotorCollection | None = None
    dto_type: type[DTO] | None = None  # type: ignore
    id_field: str | None = None
    field_name: str | None = None


class Method:
    def __init__(
        self,
        source: Callable,
        **params: str | tuple[str, ...],
    ) -> None:
        self.source: Callable = source
        self.params: dict[str, Any] = params
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
