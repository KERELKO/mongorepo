from dataclasses import dataclass
import time
from typing import Any

from mongorepo.decorators import mongo_repository_factory
from mongorepo.classes import BaseMongoRepository

from conf import users_db


@dataclass
class UserDTO:
    username: str = ''
    password: str = ''


@mongo_repository_factory
class SimpleMongoRepository:
    class Meta:
        dto = UserDTO
        collection = users_db['users']


class DummyMongoRepository(BaseMongoRepository[UserDTO]):
    ...


def test_decorator(repo: Any) -> None:
    new_user: UserDTO = repo.create(UserDTO(username='new_user', password='34666'))
    assert new_user.username == 'new_user' and new_user.password == '34666'

    updated_user: UserDTO = repo.update(
        dto=UserDTO(username='Artorias', password='1234'), username='new_user'
    )
    assert updated_user.username == 'Artorias', updated_user.username

    user_1 = UserDTO(username='user_1', password='sekg')
    user_2 = UserDTO(username='user_2', password='ri64g')
    repo.create(user_1); repo.create(user_2)  # noqa
    for user in repo.get_all():
        assert user is not None

    user_from_get = repo.get(username='user_1')
    assert user_from_get.username == 'user_1'


if __name__ == '__main__':
    time.sleep(6)
    test_decorator(SimpleMongoRepository())
    r = DummyMongoRepository(collection=users_db['users'])
    user = r.get(username='Artorias')
    print(user)
