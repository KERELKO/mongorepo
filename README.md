# mongorepo
Simple lib for python &amp; mongodb, provides auto repository factory based on DTO type
```python
from dataclasses import dataclass
from mongorepo.decorators import mongo_repository
from mongorepo.classes import BaseMongoRepository
from conf import users_db

@dataclass
class UserDTO:
    username: str = ''
    password: str = ''

@mongo_repository
class SimpleMongoRepository:
    class Meta:
        dto = UserDTO
        collection = users_db['users']

class DummyMongoRepository(BaseMongoRepository[UserDTO]):
    ...

def test_repo(repo):
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
    decorator_repo = SimpleMongoRepository()
    test_repo(decorator_repo)
    inherited_repo = DummyMongoRepository(collection=users_db['users'])
    test_repo(inherited_repo)
```


## TODO
- [ ] Add dynamic replacement for methods
- [x] Bound DTO TypeVar to DataClass interface
- [x] Test asyncio support
- [ ] Make comfortable interface
- [x] Check if class is dataclass
- [x] Fix the problem with private methods, they cannot, be access in the instance of repo but can outside the instance
- [ ] Add more methods
- [ ] Solve problem with creation of async index
- [ ] Add setup tools and refactor imports

## After TODO
- [ ] Post it on PyPi
