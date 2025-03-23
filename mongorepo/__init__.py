"""Library for generating repositories for `MongoDB`,
* public API available in this module for example:
```
@mongorepo.repository
class A:
    ...
```
### Or
use `mongorepo.decorators` or `mongorepo.classes`.

Lib also has async support, so
you can use the same classes and decorators located in `mongorepo.asyncio`

"""
from . import decorators, exceptions
from ._base import DTO, Access, Index
from .classes import BaseAsyncMongoRepository, BaseMongoRepository
from .decorators import async_mongo_repository as async_repository
from .decorators import mongo_repository as repository
from .implements.decorator import implements
from .implements.methods import Method
from .queries import AggregationStage, Condition, Operation, UpdateModifier

__all__ = [
    'Method',
    'UpdateModifier',
    'AggregationStage',
    'Operation',
    'Condition',
    'implements',
    'BaseMongoRepository',
    'BaseAsyncMongoRepository',
    'repository',
    'async_repository',
    'Access',
    'DTO',
    'Index',
    'decorators',
    'exceptions',
]
