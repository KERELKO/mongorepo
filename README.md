# mongorepo
Simple lib for python &amp; mongodb, provides auto repository factory based on DTO type

## Example with **BaseMongoRepository**
```python
from mongorepo.classes import BaseMongoRepository
from mongorepo import use_collection


def mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> pymongo.MongoClient:
    client: pymongo.MongoClient = pymongo.MongoClient(mongo_uri)
    return client


@dataclass
class UserDTO:
    username: str = ''
    password: str = ''


@use_collection(mongo_client().users_db.users)
class SimpleMongoRepository(BaseMongoRepository[UserDTO]):
    ...


repo = SimpleMongoRepository()

new_user = UserDTO(username='admin', password='1234')
repo.add(new_user)

user = repo.get(username='admin')
print(user)  # UserDTO(username='admin', password='1234')
```

## Example with **mongorepo.async_repository**
```python
import mongorepo


def async_mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> AsyncIOMotorClient:
    async_client = AsyncIOMotorClient(mongo_uri)
    return async_client


@dataclass
class Person:
    id: str
    name: str
    skills: list[str] = field(default_factory=list)    


@mongorepo.async_repository(array_fields=['skills'])
class MongoRepository:
    class Meta:
        dto = Person
        collection = async_mongo_client().people_db.people


repo = MongoRepository()


admin = Person(id='289083', name='admin', skills=['python', 'c++', 'java', 'rust'])

await repo.add(admin)
await repo.skills__append('c', id='289083')
await repo.skills__remove('python', id='289083')

user = await repo.get(id='289083')
print(user.skills)  # ['c++', 'java', 'rust', 'c']
```

## Example with **implement** decorator
```py
from mongorepo.implement import implement
from mongorepo.implement.methods import GetMethod, AddMethod
from mongorepo import use_collection


def async_mongo_client(mongo_uri: str = 'mongodb://mongodb:27017/') -> AsyncIOMotorClient:
    async_client = AsyncIOMotorClient(mongo_uri)
    return async_client


@dataclass
class Author:
    name: str


@dataclass
class Message:
    id: str
    body: str
    author: Author


class MessageRepository(typing.Protocol):
    async def add_message(self, message: Message):
        ...

    async def get_message(self, id: str) -> Message | None:
        ...


@implement(
    GetMethod(MessageRepository.get_message, filters=['id']),
    AddMethod(MessageRepository.add_message, dto='message')
)
@use_collection(async_mongo_client().messages_db.messages)
class MongoMessageRepository:
    class Meta:
        dto = Message


repo: MessageRepository = MongoMessageRepository()


await repo.add_message(
    message=Message(id='1', body='hello', author=Author(name='friend'))
)

message = await repo.get_message(id='1')
print(message)  # Message(id='1', body='hello', author=Author(name='friend'))
```
