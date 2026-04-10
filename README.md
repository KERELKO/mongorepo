# mongorepo
Simple lib for python &amp; mongodb, provides auto repository factory based on Entity type

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


@mongorepo.async_repository(
    array_fields=['skills'],
    config=RepositoryConfig(entity_type=Person, collection=async_mongo_client().people_db.people)
)
class MongoRepository:
    ...


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
    AddMethod(MessageRepository.add_message, entity='message'),
    config=RepositoryConfig(entity_type=Message, collection=async_mongo_client().messages_db.messages)
)
class MongoMessageRepository:
    ...

repo: MessageRepository = MongoMessageRepository()


await repo.add_message(
    message=Message(id='1', body='hello', author=Author(name='friend'))
)

message = await repo.get_message(id='1')
print(message)  # Message(id='1', body='hello', author=Author(name='friend'))
```
