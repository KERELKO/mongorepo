# mongorepo
Simple lib for python &amp; mongodb, provides auto repository factory based on DTO type

## Example with class
```python
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
print(user)
UserDTO(username='admin', password='1234')
```

## Example with decorator
```python
from mongorepo.asyncio.decorators import async_mongo_repository

def async_mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> AsyncIOMotorClient:
    async_client = AsyncIOMotorClient(mongo_uri)
    return async_client

@dataclass
class Person:
    id: str
    name: str
    skills: list[str] = field(default_factory=list)    

@async_mongo_repository(array_fields=['skills'])
class MongoRepository:
    class Meta:
        dto = Person
        collection = async_mongo_client().people_db.people

repo = MongoRepository()
person = Person(id='289083', name='Artorias', skills=['python', 'c++', 'java', 'rust'])
await repo.add(person)
await repo.skills__append('c', id='289083')
await repo.skills__remove('python', id='289083')
artorias = await repo.get(id='289083')
print(artorias.skills)
['c++', 'java', 'rust', 'c']
```
