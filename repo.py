from dataclasses import dataclass
import time

from mongorepo.base import MongoDTO
from mongorepo.decorators import mongo_repository_factory

from conf import users_db


@dataclass
class UserDTO(MongoDTO):
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
user = repo.get_by_id(id=new_user._id)
print(user)
print(new_user)
