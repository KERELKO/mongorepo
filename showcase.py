from dataclasses import dataclass, field
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from mongorepo import Access, Index
from mongorepo.asyncio.decorators import async_mongo_repository
from mongorepo.decorators import mongo_repository
from conf import users_db


from mongorepo.classes import BaseMongoRepository

def mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> pymongo.MongoClient:
    client: pymongo.MongoClient = pymongo.MongoClient(mongo_uri)
    return client

@dataclass
class UserDTO:
    username: str = ''
    password: str = ''

class SimpleMongoRepository(BaseMongoRepository[UserDTO]):
    ...

repo = SimpleMongoRepository(collection=mongo_client().users_db.users)
new_user = UserDTO(username='admin', password='1234')
repo.add(new_user)
user = repo.get(username='admin')


from mongorepo.asyncio.decorators import async_mongo_repository

def async_mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> AsyncIOMotorClient:
    async_client = AsyncIOMotorClient(mongo_uri)
    return async_client

@dataclass
class Person:
    id: str
    name: str
    skills: list[str] = field(default_factory=list)    

@async_mongo_repository(array_fields=['skills'], method_access=Access.PROTECTED)
class MongoRepository:
    class Meta:
        dto = Person
        collection = async_mongo_client().people_db.people
        index = Index(field='username', name='username_index', unique=True)

repo = MongoRepository()
person = Person(id='289083', name='Artorias', skills=['python', 'c++', 'java', 'rust'])
await repo.add(person=person)
await repo.skills__append('c#', id='289083')
await repo.skills__remove('python', id='289083')
artorias = await repo.get(id='289083')
print(artorias.skills)
['c++', 'java', 'rust', 'c#']
