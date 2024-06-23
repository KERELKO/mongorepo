# type: ignore
from dataclasses import dataclass
from mongorepo.decorators import mongo_repository


def mongo_client(): ...


@dataclass
class ExampleDTO:
    title: str


# You can add or remove fields if want
@mongo_repository(get_all=False, update_field=True)
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection


from mongorepo import Access

# You want to make methods private or protected use "method_access"
@mongo_repository(method_access=Access.PROTECTED)
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection

r = Repository()
r._add(ExampleDTO())


# In Meta class you can also define index by field for a collection
@mongo_repository(get_all=False, update_field=True)
class Repository:
    class Meta:
        dto = ExampleDTO
        index = 'id'
        collection = mongo_client.db.collection

from mongorepo import Index

# If you want extended Index settings use mongorepo.Index
@mongo_repository(get_all=False, update_field=True)
class Repository:
    class Meta:
        dto = ExampleDTO
        index = Index(field='id', name='id_index', desc=True, unique=True)
        collection = mongo_client.db.collection


@dataclass
class User:
    id: str
    skills: list[str] = field(default_factory=list)    

# If you need ability to update array fields use "array_fields"
# mongo_repository will add couple methods to repository to manipulate arrays
# skills__append, skills__remove, skills__pop
@mongo_repository(array_fields=['skills'])
class Repository:
    class Meta:
        dto = User
        collection = mongo_client.db.collection

# Usage example
r = Repository()
r.add(User(id='1', skills=['a', 'b', 'c']))
r.skills__append('x', id='1')  # append 'x' to the end of the array
r.skills__remove('b', id='1')  # remove 'b' from the array
x = r.skills__pop(id='1')  # variable contains 'x'



@dataclass
class ExampleDTO:
    id: str
    workers: int
    age: int = 2024

# If you want to manipulate with integer fields use "integer_fields"
# this will add two methods for each integer field: {field}_increment and {field}_decrement
@mongo_repository(integer_fields=['workers', 'age'])
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection

# Usage example
r = Repository()
r.add(ExampleDTO(id='1', workers=13))
r.increment_workers(id='1')  # this will increment workers by 1, workers=14
r.decrement_workers(id='1')  # this will decrement workers by 1
r.increment_workers(id='1', weight=5)  # this will add 5 to workers
