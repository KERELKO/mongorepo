from dataclasses import dataclass


class MongoRepoException(Exception):
    ...


@dataclass(repr=False, eq=False)
class NoMetaException(MongoRepoException):

    def __str__(self) -> str:
        return 'Class does not have "Meta" class inside'


@dataclass(repr=False, eq=False)
class NoDTOTypeException(MongoRepoException):
    with_meta: bool = True

    def __str__(self) -> str:
        return 'DTO type was not provided' + ' in "Meta" class' if self.with_meta else ''


@dataclass(repr=False, eq=False)
class NoCollectionException(MongoRepoException):
    with_meta: bool = True

    def __str__(self) -> str:
        return 'Collection was not provided' + ' in "Meta" class' if self.with_meta else ''


class NotDataClass(MongoRepoException):
    def __str__(self) -> str:
        return 'Provided dto type does not implement dataclass interface'


@dataclass(repr=False, eq=False)
class NoSubstituteException(MongoRepoException):
    with_meta: bool = True

    def __str__(self) -> str:
        return 'Substitute was not provided' + ' in "Meta" class' if self.with_meta else ''


@dataclass(repr=False, eq=False)
class InvalidMethodNameException(MongoRepoException):
    method_name: str
    msg: str | None = None
    available_methods: tuple[str, ...] | None = None

    def __str__(self) -> str:
        if self.msg:
            return self.msg
        msg = f'Method "{self.method_name}" does not appear in mongorepo available methods'
        if self.available_methods:
            msg += f'\nAvailable methods: {self.available_methods!r}'
        return msg


@dataclass(repr=False, eq=False)
class InvalidMethodNameInSourceClassException(MongoRepoException):
    cls_method_name: str
    source_cls: type

    def __str__(self) -> str:
        return f'{self.source_cls.__name__} does have "{self.cls_method_name}" method'
