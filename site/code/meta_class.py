# type: ignore
from dataclasses import dataclass
from mongorepo.decorators import mongo_repository


def mongo_client(): ...


@dataclass
class ExampleDTO:
    id: str
    title: str

# You can define index field for a collection in Meta class
@mongo_repository
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection
        index = 'id'

from mongorepo import Index


# If you want extended Index settings use mongorepo.Index
@mongo_repository
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection
        index = Index(field='id', name='id_index', desc=True, unique=True)


# Use id_field if you want to declare id field for a dto,
# mongorepo will store generated id by MongoDB there
@mongo_repository
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection
        id_field = 'id'
