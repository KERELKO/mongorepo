from dataclasses import dataclass, field
from typing import Any

from bson import ObjectId
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient


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
    _id: ObjectId = field(default_factory=ObjectId, kw_only=True)
    dtos: list[SimpleDTO] = field(default_factory=list)


@dataclass
class DTOWithDict:
    oid: str = ''
    records: dict[str, Any] = field(default_factory=dict)


def collection_for_complicated_dto(async_client: bool = False):
    if async_client:
        return async_mongo_client()['dto_complicated_db']['dto']
    return mongo_client()['dto_complicated_db']['dto']


def collection_for_simple_dto(async_client: bool = False):
    if async_client:
        return async_mongo_client()['dto_simple_db']['dto']
    return mongo_client()['dto_simple_db']['dto']


def collection_for_dto_with_id(async_client: bool = False):
    if async_client:
        return async_mongo_client()['dto_with_id_db']['dto']
    return mongo_client()['dto_with_id_db']['dto']


def custom_collection(dto_name: str, async_client: bool = False, ):
    if async_client:
        return async_mongo_client()[f'{dto_name}_db'][dto_name]
    return mongo_client()[f'{dto_name}_db'][dto_name]
