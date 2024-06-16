Meta class is crucial if you use mongorepo decorators, Meta class it's required to define 
"dto" and "collection" it gives repository ability to effectively manipulate with data within collection


```py
# "dto" it's simpe class that impements dataclass interface,
# collection is type of pymongo.Collection
@dataclass
class ExampleDTO:

@mongo_repository(get_all=False, update_field=True)
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection
```

```py
# You can define index field for a collection in Meta class
@mongo_repository(get_all=False, update_field=True)
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection
        index = 'id'
```

```py
from mongorepo import Index

# If you want extended Index settings use mongorepo.Index
@mongo_repository(get_all=False, update_field=True)
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection
        index = Index(field='id', name='id_index', desc=True, unique=True)
```
