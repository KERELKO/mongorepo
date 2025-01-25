import inspect
from typing import Any, Callable, Protocol

from mongorepo._base import LParameter, MethodAction
from mongorepo._methods import CRUD_METHODS, INTEGER_METHODS, LIST_METHODS
from mongorepo.asyncio._methods import (
    CRUD_METHODS_ASYNC,
    INTEGER_METHODS_ASYNC,
    LIST_METHODS_ASYNC,
)


class SpecificMethod(Protocol):
    mongorepo_method: Callable
    name: str
    source: Callable
    params: dict[str, LParameter]
    action: MethodAction


class SpecificFieldMethod(SpecificMethod):
    field_name: str
    integer_weight: int | None


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


class GetMethod(Method):
    """
    ### Class that represents mongorepo `get` method
    * supports `async`, `await` syntax
    ## Usage example

    ```
    @dataclass
    class User:
        id: str

    class Repo(typing.Protocol):
        # this method can be also asynchronous
        def get(self, id: str) -> User:
            ...

    @implements(Repo, GetMethod(Repo.get, filters=['id']))
    class MongoRepo:
        class Meta:
            dto = User
            collection = db.users.users_collection

    repo = MongoRepo()
    user = repo.get(id='123')
    ```

    """

    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore
        self.action = MethodAction.GET
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class AddMethod(Method):
    """
    ### Class that represents mongorepo `add` method
    * supports `async`, `await` syntax
    ## Usage example

    ```
    @dataclass
    class User:
        name: str

    class Repo(typing.Protocol):
        # this method can be also asynchronous
        def add(self, user: User) -> User:
            ...

    @implements(Repo, AddMethod(Repo.add, dto='user'))
    class MongoRepo:
        class Meta:
            dto = User
            collection = db.users.users_collection

    repo = MongoRepo()
    added_user = repo.add(user=User(name='admin'))
    ```

    """

    def __init__(self, source: Callable, dto: str) -> None:
        super().__init__(source, **{dto: 'dto'})  # type: ignore
        self.action = MethodAction.ADD
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class UpdateMethod(Method):
    """
    ### Class that represents mongorepo `update` method
    * supports `async`, `await` syntax
    ## Usage example

    ```
    @dataclass
    class User:
        id: str
        name: str

    @dataclass
    class UpdateUser:
        name: str

    class Repo(typing.Protocol):
        # this method can be also asynchronous
        def update_user(self, id: str, update_model: UpdateUser) -> User:
            ...

    @implements(
        Repo,
        UpdateMethod(Repo.update_user, filters=['id'], dto='update_model')
    )
    class MongoRepo:
        class Meta:
            dto = User
            collection = db.users.users_collection

    repo = MongoRepo()
    updated_user: User = repo.update_user(id='123', UpdateUser(name='admin_1'))
    print(updated_user.name)  # admin_1
    ```
    ## Note
    * All fields of update model will be used to update record in DB

    ### Example:

    ```
    user = repo.get(id='1')
    print(user)  # User(name='admin', id='1')

    @dataclass
    class UpdateUser:
        id: str | None = None
        name: str | None = None

    # In this example the desired action is to update only `name` field, but
    # in practice, together with `name` will be updated `id`
    updated_user = repo.update(id='1', UpdateUser(name='creator'))
    print(updated_user)  # User(id=None, name='creator')
    ```

    """
    def __init__(self, source: Callable, dto: str, filters: list[str]) -> None:
        super().__init__(
            source, **{dto: 'dto'}, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.UPDATE
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class DeleteMethod(Method):
    """
    ### Class that represents mongorepo `delete` method
    * supports `async`, `await` syntax
    ## Usage example

    ```
    class Repo(typing.Protocol):
        # this method can be also asynchronous
        def remove_user(self, id: str) -> bool:
            ...

    @implements(Repo, DeleteMethod(Repo.remove_user, filters=['id']))
    class MongoRepo:
        class Meta:
            dto = User
            collection = db.users.users_collection

    repo = MongoRepo()
    deleted: bool = repo.remove_user(id='1')
    ```

    """
    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore
        self.action = MethodAction.DELETE
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class GetListMethod(Method):
    """
    ### Class that represents mongorepo `get_list` method
    * supports `async`, `await` syntax
    ## Usage example

    ```
    class BookRepo(typing.Protocol):
        # this method can be also asynchronous
        def get_list_of_books(self, category: str) -> list[Book]:
            ...

    @implements(
        BookRepo,
        GetListMethod(BookRepo.get_list_of_books, filters=['category'])
    )
    class MongoRepo:
        class Meta:
            dto = Book
            collection = db.books.books_collection

    repo = MongoRepo()
    books = repo.get_list_of_books(category='fiction')
    print(books)  # [Book(title='...', category='fiction'), Book(title='...', category='fiction')]
    ```

    """
    def __init__(
        self,
        source: Callable,
        filters: list[str],
        offset: str,
        limit: str,
    ) -> None:
        super().__init__(
            source, **{offset: 'offset', limit: 'limit'},  # type: ignore
            **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.GET_LIST
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class GetAllMethod(Method):
    """
    ### Class that represents mongorepo `get_all` method
    * supports `async`, `await` syntax
    ## Usage example

    ```
    class BookRepo(typing.Protocol):
        # this method can be also asynchronous
        def get_all_books(self) -> typing.Generator[Book, None]:
            ...

    @implements(
        BookRepo,
        GetAllMethod(BookRepo.get_all, filters=[])
    )
    class MongoRepo:
        class Meta:
            dto = Book
            collection = db.books.books_collection

    repo = MongoRepo()
    books = repo.get_all_books()
    print(next(books))  # Book(title='...', category='fiction')
    ```
    """

    def __init__(self, source: Callable, filters: list[str]) -> None:
        super().__init__(source, **dict.fromkeys(filters, 'filters'))  # type: ignore
        self.action = MethodAction.GET_ALL
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class AddBatchMethod(Method):
    """
    ### Class that represents mongorepo `add_batch` method
    * supports `async`, `await` syntax
    ## Usage example

    ```
    class BookRepo(typing.Protocol):
        # this method can be also asynchronous
        def add_books(self, books: list[Book]) -> None:
            ...

    @implements(
        BookRepo,
        AddBatchMethod(BookRepo.add_books, dto_list=['books'])
    )
    class MongoRepo:
        class Meta:
            dto = Book
            collection = db.books.books_collection

    repo = MongoRepo()
    repo.add_books([
        Book(title='1', category='science fiction'),
        Book(title='2', category='romance'),
    ])
    ```
    """

    def __init__(self, source: Callable, dto_list: str) -> None:
        super().__init__(source, **{dto_list: 'dto_list'})  # type: ignore
        self.action = MethodAction.ADD_BATCH
        self.mongorepo_method = (
            CRUD_METHODS_ASYNC[self.action] if self.is_async else CRUD_METHODS[self.action]
        )


class ListAppendMethod(Method):
    """### Class that represents mongorepo `list_append` method

    * supports `async`, `await` syntax
    * works this dataclasses and standard types (e.g. str, int, etc.)
    ## Usage example

    ```

    @dataclass
    class Box:
        weight: int

    @dataclas
    class Cargo:
        id: str
        boxes: list[Box]

    class CargoRepo(typing.Protocol):
        # this method can be also asynchronous
        def add_box_to_cargo(self, id: str, box: Box) -> None:
            ...

    @implements(
        CargoRepo,
        ListAppendMethod(
            CargoRepo.add_box_to_cargo,
            field_name='boxes',  # Cargo.boxes
            filters=['id'],
            value='box'
        )
    )
    class MongoRepo:
        class Meta:
            dto = Cargo
            collection = db.cargo.cargo_collection

    repo = MongoRepo()
    repo.add_box_to_cargo(id='1', box=Box(weight=5))
    cargo = repo.get(id='1')
    print(cargo)  # Cargo(id='1', boxes=[Box(weight=5)])
    ```

    """

    def __init__(self, source: Callable, field_name: str, value: str, filters: list[str]) -> None:
        super().__init__(
            source, **{value: 'value'}, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.field_name = field_name
        self.action = MethodAction.LIST_APPEND
        self.mongorepo_method = (
            LIST_METHODS_ASYNC[self.action] if self.is_async else LIST_METHODS[self.action]
        )


class ListPopMethod(Method):
    """### Class that represents mongorepo `list_pop` method

    * supports `async`, `await` syntax
    * works this dataclasses and standard types (e.g. str, int, etc.)
    ## Usage example

    ```

    @dataclass
    class Box:
        weight: int

    @dataclas
    class Cargo:
        id: str
        boxes: list[Box]

    class CargoRepo(typing.Protocol):
        # this method can be also asynchronous
        def pop_box(self, id: str) -> Box:  # or raises mongorepo.exceptions.NotFoundException
            ...

    @implements(
        CargoRepo,
        ListPopMethod(
            CargoRepo.pop_box,
            field_name='boxes',  # Cargo.boxes
            filters=['id'],
        )
    )
    class MongoRepo:
        class Meta:
            dto = Cargo
            collection = db.cargo.cargo_collection

    repo = MongoRepo()
    cargo = repo.get(id='1')
    print(cargo)  # Cargo(id='1', boxes=[Box(weight=5)])
    box = repo.pop_box(id='1')
    print(box)  # Box(weight=5)
    print(repo.get(id='id'))  # Cargo(id='1', boxes=[])
    ```

    """

    def __init__(self, source: Callable, field_name: str, filters: list[str]) -> None:
        super().__init__(
            source, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.field_name = field_name
        self.action = MethodAction.LIST_POP
        self.mongorepo_method = (
            LIST_METHODS_ASYNC[self.action] if self.is_async else LIST_METHODS[self.action]
        )


class ListRemoveMethod(Method):
    """### Class that represents mongorepo `list_remove` method

    * supports `async`, `await` syntax
    * works this dataclasses and standard types (e.g. str, int, etc.)
    ## Usage example

    ```

    @dataclass
    class Box:
        weight: int

    @dataclas
    class Cargo:
        id: str
        boxes: list[Box]

    class CargoRepo(typing.Protocol):
        # this method can be also asynchronous
        def remove_box(
            self, id: str, box: Box,
        ) -> Box:  # or raises mongorepo.exceptions.NotFoundException
            ...

    @implements(
        CargoRepo,
        ListRemoveMethod(
            CargoRepo.pop_box,
            field_name='boxes',  # Cargo.boxes
            value='box'
            filters=['id'],
        )
    )
    class MongoRepo:
        class Meta:
            dto = Cargo
            collection = db.cargo.cargo_collection

    repo = MongoRepo()
    cargo = repo.get(id='1')
    print(cargo)  # Cargo(id='1', boxes=[Box(weight=5)])
    repo.remove_box(id='1', box=Box(weight=5))
    print(repo.get(id='id'))  # Cargo(id='1', boxes=[])
    ```

    """

    def __init__(self, source: Callable, field_name: str, value: str, filters: list[str]) -> None:
        super().__init__(
            source, **{value: 'value'}, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.field_name = field_name
        self.action = MethodAction.LIST_REMOVE
        self.mongorepo_method = (
            LIST_METHODS_ASYNC[self.action] if self.is_async else LIST_METHODS[self.action]
        )


class ListGetFieldValuesMethod(Method):
    """### Class that represents mongorepo `list_field_values` method

    * supports `async`, `await` syntax
    * works this dataclasses and standard types (e.g. str, int, etc.)
    ## Usage example

    ```

    @dataclass
    class Box:
        weight: int

    @dataclas
    class Cargo:
        id: str
        boxes: list[Box]

    class CargoRepo(typing.Protocol):
        # this method can be also asynchronous
        def get_cargo_boxes(
            self, id: str, limit: int = 5,
        ) -> list[Box]:  # or raises mongorepo.exceptions.NotFoundException
            ...

    @implements(
        CargoRepo,
        ListGetFieldValuesMethod(
            CargoRepo.get_cargo_boxes,
            field_name='boxes',  # Cargo.boxes
            filters=['id'],
            limit='limit',
        )
    )
    class MongoRepo:
        class Meta:
            dto = Cargo
            collection = db.cargo.cargo_collection

    repo = MongoRepo()
    cargo = repo.get(id='1')
    print(cargo)  # Cargo(id='1', boxes=[ Box(weight=5), Box(weight=2), Box(weight=1) ])
    boxes = repo.get_cargo_boxes(id='1', limit=2))
    print(boxes)  # [ Box(weight=5), Box(weight=2) ]
    ```

    """

    def __init__(
        self,
        source: Callable,
        field_name: str,
        filters: list[str],
        offset: str | None = None,
        limit: str | None = None,
    ) -> None:
        params: dict[str, Any] = {}
        if offset:
            params[offset] = 'offset'
        if limit:
            params[limit] = 'limit'
        super().__init__(
            source,
            **params,
            **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.field_name = field_name
        self.action = MethodAction.LIST_FIELD_VALUES
        self.mongorepo_method = (
            LIST_METHODS_ASYNC[self.action] if self.is_async else LIST_METHODS[self.action]
        )


class IncrementIntegerFieldMethod(Method):
    """
    ### Class that represents mongorepo `integer_increment` method
    * supports `async`, `await` syntax
    ## Usage example

    ```

    @dataclass
    class Record:
        id: str
        views: int

    class RecordRepo(typing.Protocol):
        # this method can be also asynchronous
        def increment_views(
            self, id: str,
        ) -> None:  # or raises mongorepo.exceptions.NotFoundException
            ...

    @implements(
        RecordRepo,
        IncrementIntegerFieldMethod(
            RecordRepo.increment_views,
            field_name='views',  # Record.views
            filters=['id'],
        )
    )
    class MongoRepo:
        class Meta:
            dto = Record
            collection = db.records.record_collection

    repo = MongoRepo()
    repo.add(Record(id='1', views=1000))
    repo.increment_views(id='1')
    print(repo.get(id='1'))  # Record(id='1', views=1001)
    ```
    """

    def __init__(
        self,
        source: Callable,
        field_name: str,
        filters: list[str],
        weight: str | None = None,
    ) -> None:
        params = {} if weight is None else {weight: 'weight'}
        super().__init__(
            source, **params, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.INTEGER_INCREMENT
        self.field_name = field_name
        self.mongorepo_method = (
            INTEGER_METHODS_ASYNC[self.action] if self.is_async else INTEGER_METHODS[self.action]
        )


class DecrementIntegerFieldMethod(Method):
    """
    ### Class that represents mongorepo `integer_decrement` method
    * supports `async`, `await` syntax
    ## Usage example

    ```

    @dataclass
    class Record:
        id: str
        views: int

    class RecordRepo(typing.Protocol):
        # this method can be also asynchronous
        def decrement_views(
            self, id: str, weight: int = 5,
        ) -> None:  # or raises mongorepo.exceptions.NotFoundException
            ...

    @implements(
        RecordRepo,
        DecrementIntegerFieldMethod(
            RecordRepo.decrement_views,
            field_name='views',  # Record.views
            filters=['id'],
            weight='weight',
        )
    )
    class MongoRepo:
        class Meta:
            dto = Record
            collection = db.records.record_collection

    repo = MongoRepo()
    repo.add(Record(id='1', views=1000))
    repo.decrement_views(id='1')
    print(repo.get(id='1'))  # Record(id='1', views=995)
    repo.decrement_views(id='1', weight=95)
    print(repo.get(id='1'))  # Record(id='1', views=900)
    ```
    """

    def __init__(
        self,
        source: Callable,
        field_name: str,
        filters: list[str],
        weight: str | None = None,
    ) -> None:
        params = {} if weight is None else {weight: 'weight'}
        super().__init__(
            source, **params, **dict.fromkeys(filters, 'filters'),  # type: ignore
        )
        self.action = MethodAction.INTEGER_DECREMENT
        self.field_name = field_name
        self.mongorepo_method = (
            INTEGER_METHODS_ASYNC[self.action] if self.is_async else INTEGER_METHODS[self.action]
        )
