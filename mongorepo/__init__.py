"""
Library for generating repositories for `MongoDB`, use `mongorepo.decorators` or `mongorepo.classes`
Lib also has async support, so you can use the same classes and decorators
located in `mongorepo.asyncio`
"""
from ._base import (
    Access,
    DTO,
    Index,
)
from . import exceptions, asyncio, decorators, docs

__all__ = [
    'Access',
    'DTO',
    'Index',
    'asyncio',
    'decorators',
    'docs',
    'exceptions',
]
