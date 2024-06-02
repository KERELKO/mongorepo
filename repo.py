from dataclasses import dataclass
import time

from bson import ObjectId

from mongorepo.base import MongoDTO
from mongorepo.decorators import mongo_repository_factory

from conf import users_db


@dataclass
class UserDTO(MongoDTO):
    username: str = ''
    password: str = ''


@mongo_repository_factory
class SimpleMongoRepository:
    class Meta:
        dto = UserDTO
        collection = users_db['users']


def test(repo):
    new_user: UserDTO = repo.create(UserDTO(username='new_user', password='34666'))
    assert new_user.username == 'new_user' and new_user.password == '34666'

    retrieved_user: UserDTO = repo.get_by_id(id=new_user._id)
    assert retrieved_user._id == new_user._id

    updated_user: UserDTO = repo.update(
        dto=UserDTO(username='Artorias', password='1234', _id=ObjectId(retrieved_user._id))
    )
    assert updated_user.username == 'Artorias', updated_user.username

    is_deleted = repo.delete_by_id(id=updated_user._id)
    assert is_deleted is True

    user: UserDTO | None = repo.get_by_id(id=new_user._id)
    assert user is None

    user_1 = UserDTO(username='user_1', password='sekg')
    user_2 = UserDTO(username='user_2', password='ri64g')
    repo.create(user_1); repo.create(user_2)  # noqa
    for user in repo.get_all():
        assert user is not None

    user_from_get = repo.get(username='user_1')
    assert user_from_get.username == 'user_1'


if __name__ == '__main__':
    time.sleep(6)
    test(SimpleMongoRepository())
