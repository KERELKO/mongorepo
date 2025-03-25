import functools
import pprint
import typing as t
from dataclasses import dataclass, field

from mongorepo.utils import _get_converter, get_dataclass_type_hints


@dataclass
class Profile:
    first_name: str
    avatar: str


@dataclass
class Message:
    id: str
    body: str


@dataclass
class User:
    id: str
    username: str
    profile: Profile
    other: list[str | int]
    age: int | None = None
    friends: list['User'] = field(default_factory=list)
    messages: list[Message | None] = field(default_factory=list)


print(h := t.get_type_hints(User))
print(org := t.get_origin(h['friends']))
print((messages_or_none := t.get_args(h['messages'])[0]))
print(type(messages_or_none))
print(t.get_args(messages_or_none))
# print(type(h['friends']) is list)
# print(is_dataclass(t.get_args(h['friends'])[0]))


print(get_dataclass_type_hints(User))


test_data = {
    '_id': 'sdfgsggagjhfkljhwet8h434qhg4eiue',
    'id': '1',
    'username': 'admin',
    'profile': {'first_name': 'kyryl', 'avatar': 'https://...'},
    'other': [10, 20, 30],
    'age': 18,
    'friends': [
        {
            'id': '2',
            'username': '2',
            'profile': {'first_name': '2', 'avatar': '2'},
            'other': [],
            'age': 35,
            'friends': [],
            'messages': [{'id': 5, 'body': 'wdy'}, {'id': 8, 'body': 'ok'}],
        },
    ],
    'messages': [{'id': '1', 'body': '500 ?'}, {'id': 13, 'body': 'idk'}],
}


converter = _get_converter(User, id_field='id')
user = converter(User, test_data)
print(user)


@dataclass
class User_1:
    id: str
    username: str
    friends: list['User_1'] = field(default_factory=list)


to_user = functools.partial(_get_converter(User_1), User_1)

dct = {
    'id': '1',
    'username': 'admin',
    'friends': [
        {'id': 2, 'username': 'bob', 'friends': []},
        {
            'id': 3, 'username': 'destroyer', 'friends': [
                {'id': 4, 'username': 'top_1', 'friends': []},
            ],
        },
    ],
}
user = to_user(dct)

pprint.pprint(user)
