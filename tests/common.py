import random
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Generator

import pymongo
import pymongo.collection
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


def mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> pymongo.MongoClient:
    client: pymongo.MongoClient = pymongo.MongoClient(mongo_uri)
    return client


def async_mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> AsyncIOMotorClient:
    async_client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_uri)
    return async_client


@dataclass
class SimpleEntity:
    x: str
    y: int


@dataclass
class EntityWithID:
    x: str
    y: int
    _id: str = field(default='', kw_only=True)


@dataclass
class MultiFieldEntity:
    x: str
    y: bool = False
    name: str = 'Hello World!'
    skills: list[str] = field(default_factory=list)


@dataclass
class NestedEntity:
    title: str
    simple: SimpleEntity


@dataclass
class NestedListEntity:
    title: str = 'Nested Entity'
    dtos: list[SimpleEntity] = field(default_factory=list)


@dataclass
class DictEntity:
    oid: str = ''
    records: dict[str, Any] = field(default_factory=dict)


@dataclass
class Box:
    id: str
    value: str


@dataclass
class MixedEntity:
    id: str
    name: str
    year: int
    main_box: Box
    records: list[int] = field(default_factory=list)
    boxs: list[Box] = field(default_factory=list)


def r() -> int:
    """Returns random integer."""
    return random.randint(1, 123456789)


@asynccontextmanager
async def in_async_collection(entity: str | type) -> AsyncGenerator[AsyncIOMotorCollection, None]:
    entity_name = entity if isinstance(entity, str) else entity.__name__
    try:
        collection = async_mongo_client()[f'{entity_name}_db'][entity_name]
        yield collection
    finally:
        await collection.drop()


@contextmanager
def in_collection(entity_type: str | type) -> Generator[pymongo.collection.Collection, None, None]:
    entity_name = entity_type if isinstance(entity_type, str) else entity_type.__name__
    try:
        collection = mongo_client()[f'{entity_name}_db'][entity_name]
        yield collection
    finally:
        collection.drop()


def custom_collection(entity: str | type, async_client: bool = False):
    entity_name = entity if isinstance(entity, str) else entity.__name__
    if async_client:
        return async_mongo_client()[f'{entity_name}_db'][entity_name]
    return mongo_client()[f'{entity_name}_db'][entity_name]
