import typing as t
from dataclasses import asdict

from bson import ObjectId
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from mongorepo._base import Dataclass
from mongorepo._collections import HasCollectionProvider
from mongorepo._modifiers.base import ModifierAfter, ModifierBefore
from mongorepo.utils import _get_converter

if t.TYPE_CHECKING:
    from .interfaces import IAddMethod, IGetMethod  # noqa


class AddMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasCollectionProvider,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        converter: t.Callable[[dict[str, t.Any]], T] | None = None,
        session: ClientSession | None = None,
        id_field: str | None = None,
        **kwargs,
    ) -> None:
        self.dto_type = dto_type
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.converter = converter
        self.id_field = id_field
        self.kwargs = kwargs

    def __call__(self, dto: T) -> T:
        collection: Collection = self.owner._mongorepo_collection_provider

        for modifier_before in self.modifiers_before:
            modifier_before.modify(**{'dto': dto})

        extra = {}
        object_id = ObjectId()
        if self.id_field:
            dto.__dict__[self.id_field] = str(object_id)
            extra['_id'] = object_id
        collection.insert_one({**asdict(dto), **extra}, session=self.session)

        for modifier_after in self.modifiers_after:
            modifier_after.modify(dto)

        return dto


class GetMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasCollectionProvider,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        converter: t.Callable[[type[T], dict[str, t.Any]], T] | None = None,
        session: ClientSession | None = None,
        id_field: str | None = None,
        **kwargs,
    ) -> None:
        self.dto_type = dto_type
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.converter = converter or _get_converter(dto_type, id_field)
        self.id_field = id_field
        self.kwargs = kwargs

    def __call__(self, **filters: t.Any) -> T | None:
        collection: Collection = self.owner._mongorepo_collection_provider

        for modifier_before in self.modifiers_before:
            modifier_before.modify(**filters)

        result = collection.find_one(filters)
        dto = self.converter(self.dto_type, result) if result else None

        for modifier_after in self.modifiers_after:
            modifier_after.modify(dto)

        return dto
