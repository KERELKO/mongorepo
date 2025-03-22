from typing import Callable

from mongorepo import exceptions
from mongorepo._methods.impl import AddMethod as CallableAddMethod
from mongorepo._methods.impl import GetMethod as CallableGetMethod
from mongorepo.implements.methods import AddMethod, GetMethod, SpecificMethod


def implements_mapper(specific_method: SpecificMethod) -> Callable:
    match specific_method.__class__.__name__:
        case GetMethod.__name__:
            return CallableGetMethod
        case AddMethod.__name__:
            return CallableAddMethod
    raise exceptions.MongorepoException(
        f'Cannot map specific method {specific_method.__class__} to mongorepo implementation',
    )
