from dataclasses import dataclass, field


@dataclass(repr=False, eq=False)
class MongoRepoException(Exception):
    message: str | None = field(kw_only=True, default=None)


@dataclass(repr=False, eq=False)
class NoMetaException(MongoRepoException):

    def __str__(self) -> str:
        if self.message:
            return self.message
        return 'Class does not have "Meta" class inside'


@dataclass(repr=False, eq=False)
class NoDTOTypeException(MongoRepoException):
    with_meta: bool = True

    def __str__(self) -> str:
        if self.message:
            return self.message
        return 'DTO type was not provided' + ' in "Meta" class' if self.with_meta else ''


@dataclass(repr=False, eq=False)
class NoCollectionException(MongoRepoException):
    with_meta: bool = True

    def __str__(self) -> str:
        if self.message:
            return self.message
        return 'Collection was not provided' + ' in "Meta" class' if self.with_meta else ''


class NotDataClass(MongoRepoException):
    def __str__(self) -> str:
        if self.message:
            return self.message
        return 'Provided dto type does not implement dataclass interface'


@dataclass(repr=False, eq=False)
class InvalidMethodNameException(MongoRepoException):
    method_name: str
    available_methods: tuple[str, ...] | None = None

    def __str__(self) -> str:
        if self.message:
            return self.message
        message = f'Method "{self.method_name}" does not appear in mongorepo available methods'
        if self.available_methods:
            message += f'\nAvailable methods: {self.available_methods!r}'
        return message
