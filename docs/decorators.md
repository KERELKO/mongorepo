For now, `mongorepo` gives you two decorators for creating repositories:
`mongo_repository` and `async_mongo_repository`. They have the same functionality,
but the second one is asynchonous. The decorators have a lot of functionality.
On this page I will show all available

### Include and exclude fields

to exclude field or include field in repository just pass name of the field with `True` of `False`
to the params of decorator

```py
# You can add or remove fields if want
@mongo_repository(get_all=False, update_field=True)
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection
```

### Access

If you don't want to make generated fields public you can use `mongorepo.Access` enum  
it gives decorator required information about how to define fields in the repository.  
Pass `mongorepo.Access` value to `method_access` argument in the parameters

```py
from mongorepo import Access

@mongo_repository(method_access=Access.PRIVATE)
class Repository:
    class Meta:
        dto = ExampleDTO
        collection = mongo_client.db.collection

r = Repository()
r._add(ExampleDTO())
```

### Array fields

If you need ability to update array fields use `array_fields` parameter.  
`mongo_repository` will add couple methods to repository to manipulate arrays.  
It takes the name of the list field when creates methods

methods:
`{field}__append`, `{field}__remove`, `{field}__pop`

```py
@dataclass
class User:
    id: str
    skills: list[str] = field(default_factory=list)    

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
```

### Integer fields

If you want to manipulate with integer fields use `integer_fields`
this will add two methods for each integer field:
`increment_{field}` and `decrement_{field}`  
`field` - is the name of the dto integer field 

```py
@dataclass
class ExampleDTO:
    id: str
    workers: int
    age: int = 2024

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
```
