import typing as t
from dataclasses import asdict, is_dataclass

from bson import ObjectId
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.results import InsertManyResult, UpdateResult

from mongorepo._base import Dataclass
from mongorepo._common import HasMongorepoDict
from mongorepo.modifiers.base import ModifierAfter, ModifierBefore
from mongorepo.utils import _get_converter, get_dataclass_type_hints


class AddMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
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

    def __call__(self, dto: T) -> T:
        collection: Collection[t.Any] = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            dto = modifier_before.modify(dto)

        extra = {}
        object_id = ObjectId()
        if self.id_field:
            dto.__dict__[self.id_field] = str(object_id)
            extra['_id'] = object_id
        collection.insert_one({**asdict(dto), **extra}, session=self.session)

        for modifier_after in self.modifiers_after:
            dto = modifier_after.modify(dto)

        return dto


class AddBatchMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
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

    def __call__(self, dto_list: list[T]) -> InsertManyResult:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            dto_list = modifier_before.modify(dto_list)

        if self.id_field:
            batch: list[dict[str, t.Any]] = []
            for dto in dto_list:
                object_id = ObjectId()
                dto.__dict__[self.id_field] = str(object_id)
                batch.append({**asdict(dto), '_id': object_id})
            result = collection.insert_many(batch, session=self.session)
        else:
            result = collection.insert_many([asdict(d) for d in dto_list], session=self.session)

        for modifier_after in self.modifiers_after:
            result = modifier_after.modify(result)

        return result


class GetAllMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
        modifiers: tuple[ModifierBefore, ...] = (),
        converter: t.Callable[[type[T], dict[str, t.Any]], T] | None = None,
        session: ClientSession | None = None,
        id_field: str | None = None,
        **kwargs,
    ) -> None:
        self.dto_type = dto_type
        self.owner = owner
        self.session = session
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.converter = converter or _get_converter(dto_type, id_field)
        self.kwargs = kwargs

    def __call__(self, **filters: t.Any) -> t.Generator[T, None, None]:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            filters = modifier_before.modify(**filters)

        cursor = collection.find(filters)
        for dct in cursor:
            yield self.converter(self.dto_type, dct)


class GetListMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
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
        self.kwargs = kwargs

    def __call__(self, offset: int = 0, limit: int = 20, **filters: t.Any) -> list[T]:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            offset, limit, filters = modifier_before.modify(offset, limit, **filters)

        cursor = collection.find(filter=filters).skip(offset).limit(limit)
        result = [self.converter(self.dto_type, doc) for doc in cursor]

        for modifier_after in self.modifiers_after:
            result = modifier_after.modify(result)

        return result


class GetMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
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
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            filters = modifier_before.modify(**filters)

        result = collection.find_one(filters)
        dto = self.converter(self.dto_type, result) if result else None

        for modifier_after in self.modifiers_after:
            dto = modifier_after.modify(dto)

        return dto


class DeleteMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: ClientSession | None = None,
        **kwargs,
    ) -> None:
        self.dto_type = dto_type
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    def __call__(self, **filters: t.Any) -> bool:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            filters = modifier_before.modify(**filters)

        deleted = collection.find_one_and_delete(filters, session=self.session)

        for modifier_after in self.modifiers_after:
            deleted = modifier_after.modify(deleted)

        return True if deleted else False


class UpdateMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
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
        self.kwargs = kwargs

    def __call__(self, dto: T, **filters: t.Any) -> T | None:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            dto, filters = modifier_before.modify(dto, **filters)

        data: dict[str, dict[str, t.Any]] = {'$set': {}}
        for field, value in asdict(dto).items():
            data['$set'][field] = value
        updated_document: dict[str, t.Any] | None = collection.find_one_and_update(
            filter=filters, update=data, return_document=True, session=self.session,
        )

        result = self.converter(self.dto_type, updated_document) if updated_document else None

        for modifier_after in self.modifiers_after:
            result = modifier_after.modify(result)

        return result


class UpdateListFieldMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
        field_name: str,
        action: t.Literal['$push', '$pull'],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: ClientSession | None = None,
        id_field: str | None = None,
        **kwargs,
    ) -> None:
        self.dto_type = dto_type
        self.field_name = field_name
        self.field_type = get_dataclass_type_hints(dto_type).get(field_name, None)
        self.owner = owner
        self.action = action
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.id_field = id_field
        self.kwargs = kwargs

    def __call__(self, value: t.Any, **filters: t.Any) -> UpdateResult:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            value, filters = modifier_before.modify(value, **filters)

        value = value if not is_dataclass(self.field_type) else asdict(value)

        res = collection.update_one(
            filter=filters, update={self.action: {self.field_name: value}}, session=self.session,
        )

        for modifier_aftert in self.modifiers_after:
            res = modifier_aftert.modify(res)

        return res


class AppendListMethod[T: Dataclass](UpdateListFieldMethod[T]):
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
        field_name: str,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: ClientSession | None = None,
        id_field: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            dto_type=dto_type,
            owner=owner,
            field_name=field_name,
            action='$push',
            modifiers=modifiers,
            session=session,
            id_field=id_field,
            **kwargs,
        )

    def __call__(self, value: t.Any, **filters: t.Any) -> UpdateResult:
        return super().__call__(value, **filters)


class RemoveListMethod[T: Dataclass](UpdateListFieldMethod[T]):
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
        field_name: str,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: ClientSession | None = None,
        id_field: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            dto_type=dto_type,
            owner=owner,
            field_name=field_name,
            action='$pull',
            modifiers=modifiers,
            session=session,
            id_field=id_field,
            **kwargs,
        )

    def __call__(self, value: t.Any, **filters: t.Any) -> UpdateResult:
        return super().__call__(value, **filters)


class GetListValuesMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
        field_name: str,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: ClientSession | None = None,
        **kwargs,
    ) -> None:
        self.dto_type = dto_type
        self.field_name = field_name
        fields = get_dataclass_type_hints(dto_type)
        self.field_type = fields.get(field_name, None)
        self.owner = owner
        self.field_converter = None
        if is_dataclass(self.field_type):
            self.field_converter = _get_converter(fields[field_name])
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    def __call__(self, offset: int, limit: int, **filters: t.Any) -> list[T] | list[t.Any] | None:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            offset, limit, filters = modifier_before.modify(offset, limit, **filters)

        document = collection.find_one(
            filters, {self.field_name: {'$slice': [offset, limit]}},
        )
        if document is None:
            result = None

        elif is_dataclass(self.field_type):
            result = [
                self.field_converter(self.field_type, d)  # type: ignore
                for d in document[self.field_name]
            ]
        else:
            result = document[self.field_name]

        for modifier_aftert in self.modifiers_after:
            result = modifier_aftert.modify(result)

        return result


class PopListMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
        field_name: str,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: ClientSession | None = None,
        **kwargs,
    ) -> None:
        self.dto_type = dto_type
        self.field_name = field_name
        self.owner = owner
        fields = get_dataclass_type_hints(dto_type)
        self.field_type = fields.get(field_name, None)
        self.owner = owner
        self.field_converter = None
        if is_dataclass(self.field_type):
            self.field_converter = _get_converter(fields[field_name])
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    def __call__(self, **filters: t.Any) -> T | t.Any:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            filters = modifier_before.modify(**filters)

        document = collection.find_one_and_update(
            filter=filters, update={'$pop': {self.field_name: 1}}, session=self.session,
        )
        if document is None:
            result = None
        elif is_dataclass(self.field_type):
            result = self.field_converter(  # type: ignore
                self.field_type, document[self.field_name][-1],  # type: ignore[arg-type]
            )
        else:
            result = document[self.field_name][-1]

        for modifier_aftert in self.modifiers_after:
            result = modifier_aftert.modify(result)

        return result


class IncrementIntegerFieldMethod[T: Dataclass]:
    def __init__(
        self,
        dto_type: type[T],
        owner: HasMongorepoDict[ClientSession, Collection],
        field_name: str,
        weight: int = 1,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: ClientSession | None = None,
        id_field: str | None = None,
        **kwargs,
    ) -> None:
        self.field_name = field_name
        self.owner = owner
        self.weight = weight
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    def __call__(self, weight: int | None = None, **filters) -> UpdateResult:
        collection: Collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            weight, filters = modifier_before.modify(weight, **filters)

        w = weight if weight is not None else self.weight
        result = collection.update_one(
            filter=filters, update={'$inc': {self.field_name: w}}, session=self.session,
        )

        for modifier_aftert in self.modifiers_after:
            result = modifier_aftert.modify(result)

        return result
