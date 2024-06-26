import inspect
from typing import Callable

from mongorepo._methods import METHOD_NAME__CALLABLE
from mongorepo import exceptions
from mongorepo.utils import _get_meta_attributes, raise_exc
from ._methods import substitute_method


def implements(generic_cls: type) -> Callable:
    def wrapper(cls) -> type:
        return _handle_implements(generic_cls=generic_cls, cls=cls)
    return wrapper


def _handle_implements(generic_cls: type, cls: type) -> type:
    attrs = _get_meta_attributes(cls)
    substitute = attrs['substitute'] if attrs['substitute'] is not None else raise_exc(
        exceptions.MongoRepoException(message='No "substitue" in Meta class')
    )
    dto_type = attrs['dto']
    collection = attrs['collection']
    id_field = attrs['id_field']
    for mongorepo_method_name, generic_method_name in substitute.items():
        generic_method = getattr(generic_cls, generic_method_name, None)

        if generic_method is None or not inspect.ismethod(generic_method):
            raise exceptions.InvalidMethodNameException(generic_method_name)

        if mongorepo_method_name not in METHOD_NAME__CALLABLE:
            raise exceptions.InvalidMethodNameException(mongorepo_method_name)

        mongorepo_method: Callable = METHOD_NAME__CALLABLE[mongorepo_method_name](
            dto_type=dto_type, collection=collection, id_field=id_field
        )
        setattr(
            generic_cls, generic_method_name,
            substitute_method(
                mongorepo_method,
                generic_method,
                dto_type,
                collection,
                id_field=id_field,
            ),
        )

    return cls
