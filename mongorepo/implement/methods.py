import inspect
from typing import Any, Callable, Protocol

from mongorepo.modifiers.base import ModifierAfter, ModifierBefore

from ._types import LParameter, MethodAction, ParameterEnum

Modifiers = list[ModifierBefore | ModifierAfter]


class FieldAlias:
    """Class that allow to set alias for `dataclass` field
    ### Usage example:
    ```
    @dataclass
    class User:
        name: str

    #                 User.name = username
    username_alias = FieldAlias('name', 'username')

    class UserRepository(ABC):
        @abstractmethod
        def get_user(self, username: str) -> User | None:
            ...

    @implement(GetMethod(UserRepository.get_user, filters=[username_alias]))
    class MongoUserRepository:
        ...

    repo: UserRepository = MongoUserRepository()
    user = repo.get_user(username='admin')
    print(user)  # User(name='admin')
    ```
    """

    __slots__ = ('name', 'aliases')

    def __init__(self, field: str, *aliases: str) -> None:
        self.name = field
        self.aliases = aliases

    def is_alias(self, string: str) -> bool:
        return string in self.aliases

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if isinstance(other, FieldAlias):
            return self.name == other.name and self.aliases == other.aliases
        return False

    def __repr__(self) -> str:
        aliases = ', '.join([f'"{a}"' for a in self.aliases])
        return f'{self.__class__.__name__}("{self.name}", {aliases})'

    def __str__(self) -> str:
        return self.name


class _ManageMethodFiltersMixin:
    @staticmethod
    def manage_filters(filters: list[str | FieldAlias]) -> dict[str | ParameterEnum, Any]:
        params = {f: ParameterEnum.FILTER for f in filters if isinstance(f, str)}
        aliases = {
            ParameterEnum.FILTER_ALIAS: dict.fromkeys(a.aliases, a.name)
            for a in filters if isinstance(a, FieldAlias)
        }
        return {**params, **aliases}  # type: ignore


class SpecificMethod(Protocol):
    """Protocol for specific methods.

    ### Implementations::

        | import from               | class
        mongorepo.implement.methods.GetMethod
        mongorepo.implement.methods.GetListMethod
        mongorepo.implement.methods.GetAllMethod
        mongorepo.implement.methods.AddMethod
        mongorepo.implement.methods.AddBatchMethod
        mongorepo.implement.methods.UpdateMethod
        mongorepo.implement.methods.DeleteMethod

        mongorepo.implement.methods.IncrementIntegerFieldMethod

        mongorepo.implement.methods.ListAppendMethod
        mongorepo.implement.methods.ListPopMethod
        mongorepo.implement.methods.ListRemoveMethod
        mongorepo.implement.methods.ListGetFieldValuesMethod

    """
    name: str
    source: Callable
    params: dict[str, LParameter]
    action: MethodAction
    modifiers: Modifiers

    @property
    def is_async(self) -> bool:
        ...


class SpecificFieldMethod(SpecificMethod):
    field_name: str
    integer_weight: int | None


class Method:
    """Base class that represents mongorepo method."""

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


class GetMethod(Method, _ManageMethodFiltersMixin):
    """Represents the `get` method in a Mongo repository.

    This method retrieves a single document from the database using specified filters.
    Supports both synchronous and asynchronous execution.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions

    ## Usage Example:
    ```python
    @dataclass
    class User:
        id: str

    class Repo(typing.Protocol):
        def get(self, id: str) -> User:
            ...

    @implement(GetMethod(Repo.get, filters=['id']))
    class MongoRepo:
        class Meta:
            dto = User
            collection = mongo_client().users.users_collection

    repo = MongoRepo()
    user = repo.get(id='123')
    ```

    """

    def __init__(
        self,
        source: Callable,
        filters: list[FieldAlias | str],
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(source, **self.manage_filters(filters))  # type: ignore
        self.action = MethodAction.GET
        self.modifiers = modifiers or []


class AddMethod(Method):
    """Represents the `add` method in a Mongo repository.

    This method inserts a new document into the database.
    Supports both synchronous and asynchronous execution.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support asynchronous functions

    ## Usage Example:
    ```python
    @dataclass
    class User:
        name: str

    class Repo(typing.Protocol):
        def add(self, user: User) -> User:
            ...

    @implement(AddMethod(Repo.add, dto='user'))
    class MongoRepo:
        class Meta:
            dto = User
            collection = mongo_client().users.users_collection

    repo = MongoRepo()
    added_user = repo.add(user=User(name='admin'))
    ```

    """

    def __init__(
        self,
        source: Callable,
        dto: str,
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(source, **{dto: 'dto'})  # type: ignore
        self.action = MethodAction.ADD
        self.modifiers = modifiers or []


class UpdateMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents mongorepo `update` method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions

    ## Usage example:
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

    @implement(UpdateMethod(Repo.update_user, filters=['id'], dto='update_model'))
    class MongoRepo:
        class Meta:
            dto = User
            collection = mongo_client().users.users_collection

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

    # To avoid this use UpdateSkipModifier
    # (from mongorepo.modifiers import UpdateSkipModifier) class
    @implement(
        UpdateMethod(modifiers=[UpdateSkipModifier(skip_if_value=None)], ...)
    )
    class MongoRepo: ...

    updated_user = repo.update(id='1', UpdateUser(name='creator'))
    print(updated_user)  # User(id='1', name='creator')
    ```

    """
    def __init__(
        self,
        source: Callable,
        dto: str,
        filters: list[FieldAlias | str],
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(
            source, **{dto: 'dto'}, **self.manage_filters(filters),  # type: ignore
        )
        self.action = MethodAction.UPDATE
        self.modifiers = modifiers or []


class DeleteMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents mongorepo `delete` method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions
    ## Usage example:

    ```
    class Repo(typing.Protocol):
        # this method can be also asynchronous
        def remove_user(self, id: str) -> bool:
            ...

    @implement(DeleteMethod(Repo.remove_user, filters=['id']))
    class MongoRepo:
        class Meta:
            dto = User
            collection = mongo_client().users.users_collection

    repo = MongoRepo()
    deleted: bool = repo.remove_user(id='1')  # True
    ```

    """
    def __init__(
        self,
        source: Callable,
        filters: list[FieldAlias | str],
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(source, **self.manage_filters(filters))
        self.action = MethodAction.DELETE
        self.modifiers = modifiers or []


class GetListMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents mongorepo `get_list` method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions
    ## Usage example:
    ```
    class BookRepo(typing.Protocol):
        # this method can be also asynchronous
        def get_list_of_books(self, category: str) -> list[Book]:
            ...

    @implement(GetListMethod(BookRepo.get_list_of_books, filters=['category']))
    class MongoRepo:
        class Meta:
            dto = Book
            collection = mongo_client().books.books_collection

    repo = MongoRepo()
    books = repo.get_list_of_books(category='fiction')
    print(books)  # [Book(title='...', category='fiction'), Book(title='...', category='fiction')]
    ```

    """
    def __init__(
        self,
        source: Callable,
        filters: list[FieldAlias | str],
        offset: str,
        limit: str,
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(
            source, **{offset: 'offset', limit: 'limit'},  # type: ignore
            **self.manage_filters(filters),
        )
        self.action = MethodAction.GET_LIST
        self.modifiers = modifiers or []


class GetAllMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents mongorepo `get_all` method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions

    ## Usage example:
    ```
    class BookRepo(typing.Protocol):
        def get_all_books(self) -> typing.Generator[Book, None, None]:
            ...

        async def get_all_books_async(self, category: str) -> typing.AsyncGenerator[Book, None]:
            ...

    @implement(
        GetAllMethod(BookRepo.get_all_books, filters=[]),
        GetAllMethod(BookRepo.get_all_books_async, filters=['category'])
    )
    class MongoRepo:
        class Meta:
            dto = Book
            collection = mongo_client().books.books_collection

    repo = MongoRepo()
    books = repo.get_all_books()
    print(next(books))  # Book(title='...', category='fiction')

    async for book in repo.get_all_books_async(category='fiction'):
        print(book)  # Book(title='...', category='fiction')
    ```

    """

    def __init__(
        self,
        source: Callable,
        filters: list[FieldAlias | str],
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(source, **self.manage_filters(filters))
        self.action = MethodAction.GET_ALL
        self.modifiers = modifiers or []


class AddBatchMethod(Method):
    """Class that represents mongorepo `add_batch` method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support asynchronous functions

    ## Usage example:
    ```
    class BookRepo(typing.Protocol):
        # this method can be also asynchronous
        def add_books(self, books: list[Book]) -> None:
            ...

    @implement(AddBatchMethod(BookRepo.add_books, dto_list=['books']))
    class MongoRepo:
        class Meta:
            dto = Book
            collection = mongo_client().books.books_collection

    repo = MongoRepo()
    repo.add_books([
        Book(title='1', category='science fiction'),
        Book(title='2', category='romance'),
    ])
    ```

    """

    def __init__(
        self,
        source: Callable,
        dto_list: str,
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(source, **{dto_list: 'dto_list'})  # type: ignore
        self.action = MethodAction.ADD_BATCH
        self.modifiers = modifiers or []


class ListAppendMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents `list.append()` as mongorepo method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions
    * Works with dataclass types and standard types (e.g. str, int, etc.)

    ## Usage example:
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

    @implement(
        ListAppendMethod(
            CargoRepo.add_box_to_cargo,
            field_name='boxes',  # Cargo.boxes
            filters=['id'],
            value='box'
        ),
        ...
    )
    class MongoRepo:
        class Meta:
            dto = Cargo
            collection = mongo_client().cargo.cargo_collection

    repo = MongoRepo()
    repo.add_box_to_cargo(id='1', box=Box(weight=5))
    cargo = repo.get(id='1')
    print(cargo)  # Cargo(id='1', boxes=[Box(weight=5)])
    ```

    """

    def __init__(
        self,
        source: Callable,
        field_name: str,
        value: str,
        filters: list[FieldAlias | str],
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(
            source, **{value: 'value'}, **self.manage_filters(filters),  # type: ignore
        )
        self.field_name = field_name
        self.action = MethodAction.LIST_APPEND
        self.modifiers = modifiers or []


class ListPopMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents `list.pop()` as mongorepo method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions
    * Works with dataclass types and standard types (e.g. str, int, etc.)

    ## Usage example:
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

    @implement(
        ListPopMethod(
            CargoRepo.pop_box,
            field_name='boxes',  # Cargo.boxes
            filters=['id'],
        ),
        ...
    )
    class MongoRepo:
        class Meta:
            dto = Cargo
            collection = mongo_client().cargo.cargo_collection

    repo = MongoRepo()
    cargo = repo.get(id='1')
    print(cargo)  # Cargo(id='1', boxes=[Box(weight=5)])
    box = repo.pop_box(id='1')
    print(box)  # Box(weight=5)
    print(repo.get(id='id'))  # Cargo(id='1', boxes=[])
    ```

    """

    def __init__(
        self,
        source: Callable,
        field_name: str,
        filters: list[FieldAlias | str],
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(
            source, **self.manage_filters(filters),
        )
        self.field_name = field_name
        self.action = MethodAction.LIST_POP
        self.modifiers = modifiers or []


class ListRemoveMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents `list.remove()` as mongorepo method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions
    * Works with dataclass types and standard types (e.g. str, int, etc.)

    ## Usage example:
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
        ) -> Box:
            ...

    @implement(
        ListRemoveMethod(
            CargoRepo.pop_box,
            field_name='boxes',  # Cargo.boxes
            value='box'
            filters=['id'],
        ),
        ...
    )
    class MongoRepo:
        class Meta:
            dto = Cargo
            collection = mongo_client().cargo.cargo_collection

    repo = MongoRepo()
    cargo = repo.get(id='1')
    print(cargo)  # Cargo(id='1', boxes=[Box(weight=5)])
    repo.remove_box(id='1', box=Box(weight=5))
    print(repo.get(id='id'))  # Cargo(id='1', boxes=[])
    ```
    ## Note
    By default mongorepo return `InsertResult` as execution result of this method, if you want
    to return `Box` as in the exampple above you need to write custom modifier

    """

    def __init__(
        self,
        source: Callable,
        field_name: str,
        value: str,
        filters: list[FieldAlias | str],
        modifiers: Modifiers | None = None,
    ) -> None:
        super().__init__(
            source, **{value: 'value'}, **self.manage_filters(filters),  # type: ignore
        )
        self.field_name = field_name
        self.action = MethodAction.LIST_REMOVE
        self.modifiers = modifiers or []


class ListGetFieldValuesMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents `list[offset:limit]` as mongorepo method.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions
    * Works with dataclass types and standard types (e.g. str, int, etc.)

    ## Usage example:
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
        ) -> list[Box]:
            ...

    @implement(
        ListGetFieldValuesMethod(
            CargoRepo.get_cargo_boxes,
            field_name='boxes',  # Cargo.boxes
            filters=['id'],
            limit='limit',
            # offset='...',
        ),
        ...
    )
    class MongoRepo:
        class Meta:
            dto = Cargo
            collection = mongo_client().cargo.cargo_collection

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
        filters: list[FieldAlias | str],
        offset: str | None = None,
        limit: str | None = None,
        modifiers: Modifiers | None = None,
    ) -> None:
        params: dict[str, Any] = {}
        if offset:
            params[offset] = 'offset'
        if limit:
            params[limit] = 'limit'
        super().__init__(
            source,
            **params,
            **self.manage_filters(filters),
        )
        self.field_name = field_name
        self.action = MethodAction.LIST_FIELD_VALUES
        self.modifiers = modifiers or []


class IncrementIntegerFieldMethod(Method, _ManageMethodFiltersMixin):
    """Class that represents incrementation of MongoDB integer field.

    ### Features
    * Support modifiers
    (:class:`mongorepo.modifiers.ModifierBefore`, :class:`mongorepo.modifiers.ModifierAfter`)
    * Support :class:`FieldAlias`
    * Support asynchronous functions

    ## Usage example:
    ```

    @dataclass
    class Record:
        id: str
        views: int

    class RecordRepo(typing.Protocol):
        # this method can be also asynchronous
        def increment_views(
            self, id: str,
        ) -> None:
            ...

    @implement(
        IncrementIntegerFieldMethod(
            RecordRepo.increment_views,
            field_name='views',  # Record.views
            filters=['id'],
        ),
        ...
    )
    class MongoRepo:
        class Meta:
            dto = Record
            collection = mongo_client().records.record_collection

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
        filters: list[FieldAlias | str],
        weight: str | None = None,
        default_weight_value: int = 1,
        modifiers: Modifiers | None = None,
    ) -> None:
        params = {} if weight is None else {weight: 'weight'}
        super().__init__(
            source, **params, **self.manage_filters(filters),  # type: ignore
        )
        self.action = MethodAction.INTEGER_INCREMENT
        self.field_name = field_name
        self.integer_weight = default_weight_value
        self.modifiers = modifiers or []
