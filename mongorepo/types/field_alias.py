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
