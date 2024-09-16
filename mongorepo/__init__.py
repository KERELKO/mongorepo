"""Library for generating repositories for `MongoDB`, use
`mongorepo.decorators` or `mongorepo.classes`.

Lib also has async support, so
you can use the same classes and decorators located in `mongorepo.asyncio`

"""
from . import asyncio, decorators, docs, exceptions
from ._base import DTO, Access, Index

__all__ = [
    'Access',
    'DTO',
    'Index',
    'asyncio',
    'decorators',
    'docs',
    'exceptions',
]
