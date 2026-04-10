from typing import Any, AsyncGenerator, Literal

from motor.motor_asyncio import (
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
)
from pymongo.results import InsertManyResult, UpdateResult

from mongorepo.modifiers.base import ModifierAfter, ModifierBefore
from mongorepo.types.base import ToDocumentConverter, ToEntityConverter
from mongorepo.types.field import Field
from mongorepo.types.mongorepo_dict import HasMongorepoDict


class AddMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        to_document_converter: ToDocumentConverter[T],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.to_document_converter = to_document_converter
        self.kwargs = kwargs

    async def __call__(self, entity: T) -> T:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            entity = modifier_before.modify(entity=entity)

        await collection.insert_one({**self.to_document_converter(entity)}, session=self.session)

        for modifier_after in self.modifiers_after:
            entity = modifier_after.modify(entity)

        return entity


class AddBatchMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        to_document_converter: ToDocumentConverter[T],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.to_document_converter = to_document_converter
        self.kwargs = kwargs

    async def __call__(self, entity_list: list[T]) -> InsertManyResult:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            entity_list = modifier_before.modify(entity_list=entity_list)

        result = await collection.insert_many(
            [self.to_document_converter(d) for d in entity_list], session=self.session,
        )

        for modifier_after in self.modifiers_after:
            result = modifier_after.modify(result)

        return result


class GetAllMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        to_entity_converter: ToEntityConverter[T],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.owner = owner
        self.session = session
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.to_entity = to_entity_converter
        self.kwargs = kwargs

    async def __call__(self, **filters: Any) -> AsyncGenerator[T, None]:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            filters = modifier_before.modify(**filters)

        cursor = collection.find(filters)
        async for data in cursor:
            entity = self.to_entity(data, self.entity_type)

            for modifier_after in self.modifiers_after:
                entity = modifier_after.modify(entity)

            yield entity


class GetListMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        to_entity_converter: ToEntityConverter[T],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.to_entity = to_entity_converter
        self.kwargs = kwargs

    async def __call__(self, offset: int = 0, limit: int = 20, **filters: Any) -> list[T]:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            offset, limit, filters = modifier_before.modify(
                offset, limit, **filters,
            )

        cursor = collection.find(filter=filters).skip(offset).limit(limit)
        result = [self.to_entity(doc, self.entity_type) async for doc in cursor]

        for modifier_after in self.modifiers_after:
            result = modifier_after.modify(result)

        return result


class GetMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        to_entity_converter: ToEntityConverter[T],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.to_entity = to_entity_converter
        self.kwargs = kwargs

    async def __call__(self, **filters: Any) -> T | None:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            filters = modifier_before.modify(**filters)

        result = await collection.find_one(filters)
        entity = self.to_entity(result, self.entity_type) if result else None

        for modifier_after in self.modifiers_after:
            entity = modifier_after.modify(entity)

        return entity


class DeleteMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    async def __call__(self, **filters: Any) -> bool:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            filters = modifier_before.modify(**filters)

        deleted = await collection.find_one_and_delete(filters, session=self.session)

        for modifier_after in self.modifiers_after:
            deleted = modifier_after.modify(deleted)

        return True if deleted else False


class UpdateMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        to_entity_converter: ToEntityConverter[T],
        to_document_converter: ToDocumentConverter[T],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.owner = owner
        self.session: AsyncIOMotorClientSession | None = None
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.to_document_converter = to_document_converter
        self.to_entity_converter = to_entity_converter
        self.kwargs = kwargs

    async def __call__(self, entity: T, **filters: Any) -> T | None:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            entity, filters = modifier_before.modify(entity=entity, **filters)

        data: dict[str, dict[str, Any]] = {'$set': {}}
        for field, value in self.to_document_converter(entity).items():
            data['$set'][field] = value

        updated_document: dict[str, Any] | None = await collection.find_one_and_update(
            filter=filters, update=data, return_document=True, session=self.session,
        )

        result = self.to_entity_converter(
            updated_document, self.entity_type,
        ) if updated_document else None

        for modifier_after in self.modifiers_after:
            result = modifier_after.modify(result)

        return result


class UpdateListFieldMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        target_field: Field,
        action: Literal['$push', '$pull'],
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.target_field = target_field
        self.owner = owner
        self.action = action
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    async def __call__(self, value: Any, **filters: Any) -> UpdateResult:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            value, filters = modifier_before.modify(value, **filters)

        res = await collection.update_one(
            filter=filters,
            update={self.action: {self.target_field.name: self.target_field.to_document(value)}},
            session=self.session,
        )

        for modifier_aftert in self.modifiers_after:
            res = modifier_aftert.modify(res)

        return res


class AppendListMethodAsync[T](UpdateListFieldMethodAsync[T]):
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        target_field: Field,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            entity_type=entity_type,
            owner=owner,
            target_field=target_field,
            action='$push',
            modifiers=modifiers,
            session=session,
            **kwargs,
        )

    async def __call__(self, value: Any, **filters: Any) -> UpdateResult:
        return await super().__call__(value, **filters)


class RemoveListMethodAsync[T](UpdateListFieldMethodAsync[T]):
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        target_field: Field,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            entity_type=entity_type,
            owner=owner,
            target_field=target_field,
            action='$pull',
            modifiers=modifiers,
            session=session,
            **kwargs,
        )

    async def __call__(self, value: Any, **filters: Any) -> UpdateResult:
        return await super().__call__(value, **filters)


class GetListValuesMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        target_field: Field,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.target_field = target_field
        self.owner = owner
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    async def __call__(
        self, offset: int = 0, limit: int = 20, **filters: Any,
    ) -> list[T] | list[Any] | None:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            offset, limit, filters = modifier_before.modify(
                offset, limit, **filters,
            )

        document = await collection.find_one(
            filters, {self.target_field.name: {'$slice': [offset, limit]}},
        )
        if document is None:
            result = None
        else:
            result = [
                self.target_field.to_value(d)
                for d in document[self.target_field.name]
            ]

        for modifier_aftert in self.modifiers_after:
            result = modifier_aftert.modify(result)

        return result


class PopListMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        target_field: Field,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.entity_type = entity_type
        self.target_field = target_field
        self.owner = owner
        self.field_converter = None
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    async def __call__(self, **filters: Any) -> T | Any:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            filters = modifier_before.modify(**filters)

        document = await collection.find_one_and_update(
            filter=filters, update={'$pop': {self.target_field.name: 1}}, session=self.session,
        )
        if document is None:
            result = None
        else:
            result = self.target_field.to_value(document[self.target_field.name][-1])

        for modifier_aftert in self.modifiers_after:
            result = modifier_aftert.modify(result)

        return result


class IncrementIntegerFieldMethodAsync[T]:
    def __init__(
        self,
        entity_type: type[T],
        owner: HasMongorepoDict[AsyncIOMotorClientSession, AsyncIOMotorCollection],
        target_field: Field,
        weight: int = 1,
        modifiers: tuple[ModifierBefore | ModifierAfter, ...] = (),
        session: AsyncIOMotorClientSession | None = None,
        **kwargs,
    ) -> None:
        self.target_field = target_field
        self.owner = owner
        self.weight = weight
        self.session = session
        self.modifiers_after = [m for m in modifiers if isinstance(m, ModifierAfter)]
        self.modifiers_before = [m for m in modifiers if isinstance(m, ModifierBefore)]
        self.kwargs = kwargs

    async def __call__(self, weight: int | None = None, **filters) -> UpdateResult:
        collection = self.owner.__mongorepo__['collection_provider'].provide()

        for modifier_before in self.modifiers_before:
            weight, filters = modifier_before.modify(weight, **filters)

        w = weight if weight is not None else self.weight
        result = await collection.update_one(
            filter=filters, update={'$inc': {self.target_field.name: w}}, session=self.session,
        )

        for modifier_aftert in self.modifiers_after:
            result = modifier_aftert.modify(result)

        return result
