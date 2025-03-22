import typing as t
from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import MongoClient
from pymongo.collection import Collection

from mongorepo._base import Dataclass
from mongorepo._collections import COLLECTION_PROVIDER, CollectionProvider

C = t.TypeVar('C', Collection[t.Any], AsyncIOMotorCollection)


@dataclass
class MyDTO:
    name: str


class IGetMethod(t.Protocol):
    def __call__(self, **filters: t.Any) -> Dataclass | None:
        ...


class IMongoRepository(t.Protocol):
    get: IGetMethod


class MetaAttrs(t.Generic[C], t.TypedDict, total=False):
    dto_type: type | None
    collection: C | None


def get_meta(cls: type) -> MetaAttrs:
    meta: type | None = cls.__dict__.get('Meta', None)
    if not meta:
        return {}
    data: MetaAttrs[t.Any] = {}
    data['dto_type'] = getattr(meta, 'dto_type', None)
    data['collection'] = getattr(meta, 'collection', None)
    return data


class HasCollectionProvider(t.Protocol):
    _mongorepo_collection_provider: CollectionProvider


class GetMethod[T: Dataclass]:
    def __init__(self, decorated_cls: HasCollectionProvider, dto_type: type[T], **kwargs):
        self.decorated_cls = decorated_cls
        self.dto_type = dto_type
        self.kwargs = kwargs

    def __call__(self, **filters: t.Any) -> T | None:
        collection = self.decorated_cls._mongorepo_collection_provider[Collection]

        print(collection.__class__)

        return self.dto_type(**filters)


def handler(cls, get: bool = True) -> IMongoRepository:
    if not hasattr(cls, COLLECTION_PROVIDER):
        setattr(cls, '_mongorepo_collection_provider', CollectionProvider())
    setattr(cls, 'get', GetMethod(cls, MyDTO))
    return cls


T = t.TypeVar('T')


@t.overload
def repository(cls: type[T]) -> type[T]:
    ...


@t.overload
def repository(cls: None, get: bool = True) -> t.Callable[[type[T]], type[T]]:
    ...


def repository[T](
    cls: type[T] | None = None, get: bool = True,
) -> t.Callable[[type[T]], type[T]] | type[T]:
    def wrapper(cls: type[T]) -> type[T]:  # type: ignore
        return handler(cls, get)  # type: ignore

    if not cls:
        return wrapper
    return wrapper(cls)


class use_collection:
    def __init__(self, collection: Collection):
        self.collection = collection

    def __call__(self, cls: type) -> type:
        setattr(cls, COLLECTION_PROVIDER, CollectionProvider(self.collection))
        return cls

    def for_(self, cls: type):
        setattr(cls, COLLECTION_PROVIDER, CollectionProvider(self.collection))


col = MongoClient('bla')['bla']['bla']


@repository
class Repo:
    ...


use_collection(col).for_(Repo)
repo = Repo()
print(repo.get(name='bob'))
