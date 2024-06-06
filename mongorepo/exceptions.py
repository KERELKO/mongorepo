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
