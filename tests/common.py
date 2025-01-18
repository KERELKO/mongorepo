import random
import warnings
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Generator

import pymongo
import pymongo.collation
import pymongo.collection
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


def mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> pymongo.MongoClient:
    client: pymongo.MongoClient = pymongo.MongoClient(mongo_uri)
    return client


def async_mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> AsyncIOMotorClient:
    async_client = AsyncIOMotorClient(mongo_uri)
    return async_client


@dataclass
class SimpleDTO:
    x: str
    y: int


@dataclass
class DTOWithID:
    x: str
    y: int
    _id: str = field(default='', kw_only=True)


@dataclass
class ComplicatedDTO:
    x: str
    y: bool = False
    name: str = 'Hello World!'
    skills: list[str] = field(default_factory=list)


@dataclass
class NestedDTO:
    title: str
    simple: SimpleDTO


@dataclass
class NestedListDTO:
    title: str = 'Nested DTO'
    dtos: list[SimpleDTO] = field(default_factory=list)


@dataclass
class DictDTO:
    oid: str = ''
    records: dict[str, Any] = field(default_factory=dict)


@dataclass
class Box:
    id: str
    value: str


@dataclass
class MixDTO:
    id: str
    name: str
    year: int
    main_box: Box
    records: list[int] = field(default_factory=list)
    boxs: list[Box] = field(default_factory=list)


def collection_for_complicated_dto(async_client: bool = False):
    warnings.warn('"collection_for_complicated_dto" is deprecated, use "custom_collection" instead')
    if async_client:
        return async_mongo_client()['dto_complicated_db']['dto']
    return mongo_client()['dto_complicated_db']['dto']


def collection_for_simple_dto(async_client: bool = False):
    warnings.warn('"collection_for_simple_dto" is deprecated, use "custom_collection" instead')
    if async_client:
        return async_mongo_client()['dto_simple_db']['dto']
    return mongo_client()['dto_simple_db']['dto']


def collection_for_dto_with_id(async_client: bool = False):
    warnings.warn('"collection_for_dto_with_id" is deprecated, use "custom_collection" instead')
    if async_client:
        return async_mongo_client()['dto_with_id_db']['dto']
    return mongo_client()['dto_with_id_db']['dto']


def custom_collection(dto: str | type, async_client: bool = False):
    dto_name = dto if isinstance(dto, str) else dto.__name__
    if async_client:
        return async_mongo_client()[f'{dto_name}_db'][dto_name]
    return mongo_client()[f'{dto_name}_db'][dto_name]


def r() -> int:
    """Returns random integer."""
    return random.randint(1, 123456)


@asynccontextmanager
async def in_async_collection(dto: str | type) -> AsyncGenerator[AsyncIOMotorCollection, None]:
    dto_name = dto if isinstance(dto, str) else dto.__name__
    try:
        collection = async_mongo_client()[f'{dto_name}_db'][dto_name]
        yield collection
    finally:
        await collection.drop()


@contextmanager
def in_collection(dto: str | type) -> Generator[pymongo.collection.Collection, None, None]:
    dto_name = dto if isinstance(dto, str) else dto.__name__
    try:
        collection = mongo_client()[f'{dto_name}_db'][dto_name]
        yield collection
    finally:
        collection.drop()
