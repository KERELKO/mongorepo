This tutorial assumes that MongoDB is running on your machine


```python
from dataclasses import dataclass
from mongorepo.decorators import mongo_repository
import pymongo


def mongo_client_factory(
    mongo_uri: str = 'mongodb://mongodb:27017/'
) -> pymongo.MongoClient:
    client = pymongo.MongoClient(mongo_uri)
    return client


# Define DTO
@dataclass
class UserDTO:
    username: str = ''
    password: str = ''


# Decorate class with mongo_repository
@mongo_repository
class MongoRepository:
    class Meta:
        dto = UserDTO
        collection = mongo_client_factory()['users_db']['users_collection']


repository = MongoRepository()

# to add users to collection use method "add" and pass dto defined in Meta class 
user_1 = UserDTO(username='admin', password='1234')
user_2 = UserDTO(username='bob')
repository.add(user_1)
repository.add(user_2)

# you can find a user by fields defined in DTO
user_1: UserDTO | None = repository.get(username='admin')

# update records with "update" method
# first pass dto with data that you want to change, then search filter
updated_user_2: UserDTO | None = repository.update(
    UserDTO(username='Super Bob'), username='bob',
)

# you can also delete a user
is_deleted: bool = repository.delete(username='admin')
```
