from dataclasses import dataclass, field
import time

from bson import ObjectId

from factory import mongo_repository_factory

from conf import users_db


@dataclass
class BaseMongoDTO:
    _id: str = field(default_factory=ObjectId, kw_only=True)


@dataclass
class UserDTO(BaseMongoDTO):
    username: str
    password: str


@mongo_repository_factory
class SimpleMongoRepository:
    class Meta:
        dto = UserDTO
        collection = users_db['users']


time.sleep(8)
repo = SimpleMongoRepository()
new_user: UserDTO = repo.create(UserDTO(username='new_user', password='34666'))
user = repo.get(oid=new_user._id)
print(user)
print(new_user)
