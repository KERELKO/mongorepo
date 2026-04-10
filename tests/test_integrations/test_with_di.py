from typing import Protocol, cast

import punq  # type: ignore[import-untyped]
from dishka import Provider, Scope, make_container, provide

import mongorepo
from tests.common import SimpleEntity, mongo_client


def test_repository_with_punq_container() -> None:

    class SimpleRepository(Protocol):
        def add(self, entity: SimpleEntity):
            ...

        def get(self, x: str, y: int) -> SimpleEntity | None:
            ...

    @mongorepo.repository(config=mongorepo.RepositoryConfig(entity_type=SimpleEntity))
    class MongoSimpleRepository:
        ...

    def punq_container() -> punq.Container:
        container = punq.Container()

        collection = mongo_client()["simple_db"]["simple"]

        # Here can be possible to decorate with `mongorepo.repository`
        # and pass collection directly, but it will look slightly complicated if
        # a lot of parameters will be provided. In this case `mongorepo.provide_collection` will
        # look better
        mongorepo.provide_collection(MongoSimpleRepository, collection)
        container.register(SimpleRepository, MongoSimpleRepository)
        return container

    container = punq_container()

    repo = cast(SimpleRepository, container.resolve(SimpleRepository))

    entity = SimpleEntity(x='1', y=1)
    repo.add(entity)

    entity = repo.get(x='1', y=1)  # type: ignore[assignment]

    assert entity is not None
    assert entity.x == '1' and entity.y == 1


def test_repository_with_dishka() -> None:

    class SimpleRepository(Protocol):
        def add(self, entity: SimpleEntity):
            ...

        def get(self, x: str, y: int) -> SimpleEntity | None:
            ...

    @mongorepo.repository(config=mongorepo.RepositoryConfig(entity_type=SimpleEntity))
    class MongoSimpleRepository:
        ...

    class RepositoryProvider(Provider):
        @provide(scope=Scope.APP)
        def simple_repository(self) -> SimpleRepository:
            collection = mongo_client()["simple_db"]["simple"]
            mongorepo.provide_collection(MongoSimpleRepository, collection)
            return MongoSimpleRepository()  # type: ignore

    container = make_container(RepositoryProvider())

    repo = container.get(SimpleRepository)

    entity = SimpleEntity(x='1', y=1)
    repo.add(entity)

    entity = repo.get(x='1', y=1)  # type: ignore[assignment]

    assert entity is not None
    assert entity.x == '1' and entity.y == 1
