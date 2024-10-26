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
from . import asyncio, decorators, docs, exceptions
from ._base import DTO, Access, Index
from .asyncio.classes import AsyncBasedMongoRepository
from .asyncio.decorators import async_mongo_repository as async_repository
from .classes import BaseMongoRepository
from .decorators import implements
from .decorators import mongo_repository as repository

__all__ = [
    'implements',
    'BaseMongoRepository',
    'AsyncBasedMongoRepository',
    'repository',
    'async_repository',
    'Access',
    'DTO',
    'Index',
    'asyncio',
    'decorators',
    'docs',
    'exceptions',
]
