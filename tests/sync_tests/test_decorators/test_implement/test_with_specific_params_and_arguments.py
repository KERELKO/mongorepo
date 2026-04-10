# mypy: disable-error-code="attr-defined"
from mongorepo import RepositoryConfig
from mongorepo.implement import implement
from mongorepo.implement.methods import (
    AddMethod,
    ListAppendMethod,
    ListItemsMethod,
    ListPopMethod,
    ListRemoveMethod,
)
from tests.common import NestedListEntity, SimpleEntity, in_collection


def test_can_change_order_of_repo_parameters_and_passed_arguments() -> None:

    class IRepo:
        def add(self, entity: NestedListEntity) -> None:
            ...

        # Change order of offset and remove its default value
        def get_simple_dto_list_by_title(  # type: ignore[empty-body]
            self, offset: int, title: str, limit: int = 20,
        ) -> list[SimpleEntity]:
            ...

        def pop_dto_by_title(self, title: str) -> SimpleEntity:  # type: ignore[empty-body]
            ...

        # Set entity as a second parameter
        def append_dto_by_title(self, title: str, entity: SimpleEntity) -> None:
            ...

        def remove_dto_by_title(self, entity: SimpleEntity, title: str) -> None:
            ...

    with in_collection(NestedListEntity) as cl:
        @implement(
            AddMethod(IRepo.add, entity='entity'),
            ListItemsMethod(
                IRepo.get_simple_dto_list_by_title,
                field='dtos',
                filters=['title'],
                offset='offset',
                limit='limit',
            ),
            ListPopMethod(IRepo.pop_dto_by_title, field='dtos', filters=['title']),
            ListAppendMethod(
                IRepo.append_dto_by_title, filters=['title'], field='dtos', value='entity',
            ),
            ListRemoveMethod(
                IRepo.remove_dto_by_title, value='entity', field='dtos', filters=['title'],
            ),
            config=RepositoryConfig(entity_type=NestedListEntity, collection=cl),
        )
        class MongoRepo:
            ...

        r: IRepo = MongoRepo()  # type: ignore
        title = 'title'
        r.add(NestedListEntity(title, dtos=[SimpleEntity(x='1', y=1), SimpleEntity(x='1', y=1)]))

        _ = r.get_simple_dto_list_by_title(offset=0, title=title, limit=20)
        _ = r.get_simple_dto_list_by_title(offset=0, title=title)
        _ = r.get_simple_dto_list_by_title(limit=5, title='title', offset=1)
        _ = r.get_simple_dto_list_by_title(offset=5, title='title')

        r.append_dto_by_title(title=title, entity=SimpleEntity(x='3', y=3))
        r.append_dto_by_title(title, SimpleEntity(x='2', y=2))
        r.append_dto_by_title(entity=SimpleEntity(x='2', y=2), title=title)

        _ = r.pop_dto_by_title(title)
        _ = r.pop_dto_by_title(title=title)

        r.remove_dto_by_title(title=title, entity=SimpleEntity(x='1', y=1))
        r.remove_dto_by_title(SimpleEntity(x='1', y=3), title)
        r.remove_dto_by_title(SimpleEntity(x='1', y=1), title=title)

    assert True
