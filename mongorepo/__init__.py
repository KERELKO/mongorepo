"""
Library for generating repositories for `MongoDB`, use `mongorepo.decorators` or `mongorepo.classes`
Lib also has async support, so you can use the same classes and decorators
located in `mognorepo.asyncio`
"""
from .base import (
    Access,
    DTO,
    Index,
)
from .docs import get_available_meta_attributes, get_available_repository_methods


__all__ = [
    'Access',
    'DTO', 'Index',
    'get_available_meta_attributes',
    'get_available_repository_methods',
]
