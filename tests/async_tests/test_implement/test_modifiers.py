import pytest

from mongorepo import use_collection
from mongorepo.implement import AddMethod, FieldAlias, GetMethod, implement
from mongorepo.implement.methods import UpdateMethod
from mongorepo.modifiers.base import (
    ModifierAfter,
    ModifierBefore,
    RaiseExceptionModifier,
    UpdateSkipModifier,
)
from tests.common import Box, SimpleEntity, in_async_collection


async def test_after_modifiers():
    class CustomAfterModifier(ModifierAfter):
        def modify(self, data: SimpleEntity | None) -> SimpleEntity | None:
            if isinstance(data, SimpleEntity):
                data.x = 'Hello World'
            return data

    class NotFound(Exception):
        ...

    class Repo:
        async def get(self, dto_id: str) -> SimpleEntity | None:
            ...

        async def add(self, entity: SimpleEntity):
            ...

        async def get_custom(self, x: str) -> SimpleEntity | None:
            ...

    async with in_async_collection(SimpleEntity) as coll:
        @use_collection(coll)
        @implement(
            AddMethod(Repo.add, entity='entity'),
            GetMethod(
                Repo.get,
                filters=[FieldAlias('x', 'dto_id')],
                modifiers=[RaiseExceptionModifier(exc=NotFound, raise_when_result=None)],
            ),
            GetMethod(Repo.get_custom, filters=['x'], modifiers=[CustomAfterModifier()]),
        )
        class Mongorepo:
            class Meta:
                entity = SimpleEntity

        repo: Repo = Mongorepo()  # type: ignore

        new_dto = SimpleEntity(x='100', y=100)

        await repo.add(new_dto)

        get_dto = await repo.get(dto_id='100')
        assert new_dto == get_dto

        with pytest.raises(NotFound):
            _ = await repo.get(dto_id='0')

        hello_world = await repo.get_custom(x='100')
        assert hello_world
        assert hello_world.x == 'Hello World'


async def test_before_modifiers():
    class CustomGetBeforeModifier(ModifierBefore):
        def modify(self, id) -> dict[str, str]:
            print(f'{id=}')
            if id is None:
                raise ValueError('box_id cannot be None')
            elif not isinstance(id, str):
                raise TypeError('box_id must be str')
            return {'id': id}

    class NotFound(Exception):
        ...

    class Repo:
        async def get(self, box_id: str) -> Box:  # type: ignore[empty-body]
            ...

        async def add(self, box: Box) -> Box:  # type: ignore[empty-body]
            ...

        async def update(self, box: Box, box_id: str) -> Box:  # type: ignore[empty-body]
            ...

    not_found_mod = RaiseExceptionModifier(NotFound, None)

    async with in_async_collection(Box) as coll:
        @implement(
            GetMethod(
                Repo.get, filters=[a := FieldAlias('id', 'box_id')], modifiers=[
                    not_found_mod, CustomGetBeforeModifier(),
                ],
            ),
            AddMethod(Repo.add, entity='box'),
            UpdateMethod(
                Repo.update,
                entity='box',
                filters=[a],
                modifiers=[UpdateSkipModifier(skip_if_value=None), not_found_mod],
            ),
        )
        class Mongorepo:
            class Meta:
                entity = Box
                collection = coll
                id_field = 'id'

        repo: Repo = Mongorepo()  # type: ignore
        box = Box(id='1', value='1kg')
        added_box_id = (await repo.add(box)).id
        update_box = Box(id=None, value='2kg')  # type: ignore
        # await asyncio.sleep(1000)
        updated_box = await repo.update(update_box, box_id=added_box_id)
        assert updated_box.id == added_box_id and updated_box.value == '2kg'

        get_box = await repo.get(box_id=added_box_id)
        assert get_box.id == added_box_id and get_box.value == '2kg'

        with pytest.raises(ValueError):
            _ = await repo.get(box_id=None)  # type: ignore

        with pytest.raises(TypeError):
            _ = await repo.get(box_id=1)  # type: ignore
