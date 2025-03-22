class MongorepoException(Exception):
    def __init__(self, message: str | None = None):
        self.message = message

    def __str__(self) -> str:
        return self.message or super().__str__()


class NoMetaException(MongorepoException):
    def __str__(self) -> str:
        if self.message:
            return self.message
        return 'Class does not have "Meta" class inside'


class NoDTOTypeException(MongorepoException):
    def __init__(self, message: str | None = None, with_meta: bool = True):
        self.with_meta: bool = with_meta
        self.message = message

    def __str__(self) -> str:
        if self.message:
            return self.message
        return 'DTO type was not provided' + ' in "Meta" class' if self.with_meta else ''


class NoCollectionException(MongorepoException):
    def __init__(self, message: str | None = None, with_meta: bool = True):
        self.with_meta: bool = with_meta
        self.message = message

    def __str__(self) -> str:
        if self.message:
            return self.message
        return 'Collection was not provided' + ' in "Meta" class' if self.with_meta else ''


class NotDataClass(MongorepoException):
    def __str__(self) -> str:
        if self.message:
            return self.message
        return 'Provided dto type does not implement dataclass interface'


class InvalidMethodNameException(MongorepoException):
    def __init__(
        self,
        method_name: str,
        message: str | None = None,
        available_methods: tuple[str, ...] | None = None,
    ):
        self.message = message
        self.method_name: str = method_name
        self.available_methods: tuple[str, ...] | None = available_methods

    def __str__(self) -> str:
        if self.message:
            return self.message
        message = f'Method "{self.method_name}" does not appear in mongorepo available methods'
        if self.available_methods:
            message += f'\nAvailable methods: {self.available_methods!r}'
        return message


class TypeHintException(MongorepoException):
    def __str__(self) -> str:
        if self.message:
            return self.message
        message = 'Invalid type hint'
        return message


class NotFoundException(MongorepoException):
    def __init__(self, **filters) -> None:
        self.filters = filters

    def __str__(self) -> str:
        filters = ', '.join([f'{key}={value}' for key, value in self.filters.items()])
        return f'Document not found, filters: {filters}'


class InvalidActionException(MongorepoException):
    def __init__(self, valid_actions: list[str], action: str, message: str | None = None):
        self.message = message
        self.action: str = action
        self.valid_actions: list[str] = valid_actions

    def __str__(self) -> str:
        return (
            self.message or f'Invalid method action: {self.action}\nValid are: {self.valid_actions}'
        )
