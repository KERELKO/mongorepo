import inspect
from typing import Callable

from mongorepo import exceptions
from mongorepo._base import MethodDeps
from mongorepo.utils import _get_meta_attributes, raise_exc

from ._substitute import _substitute_method, _substitute_specific_method
from .methods import Method, SpecificMethod


def _handle_implements_custom_methods(
    base_cls: type,
    cls: type,
    **substitute: str | Callable | Method,
) -> type:
    attrs = _get_meta_attributes(cls)
    if not substitute:
        substitute = attrs['substitute'] if attrs['substitute'] is not None else raise_exc(
            exceptions.MongoRepoException(message='No "substitute" in Meta class'),
        )
    dto_type = attrs['dto']
    collection = attrs['collection']
    id_field = attrs['id_field']
    for mongorepo_method_name, _generic_method in substitute.items():
        if not isinstance(_generic_method, Method):
            if inspect.isfunction(_generic_method) or inspect.ismethod(_generic_method):
                generic_method = Method(_generic_method)

            elif isinstance(_generic_method, str):
                __generic_method: Callable | None = getattr(
                    base_cls, _generic_method, None,
                )
                if __generic_method is None or not inspect.isfunction(__generic_method):
                    raise exceptions.InvalidMethodNameException(_generic_method)
                generic_method = Method(__generic_method)  # type: ignore
        else:
            generic_method = _generic_method

        setattr(
            cls,
            generic_method.name,
            _substitute_method(
                mongorepo_method_name,
                generic_method,
                dto_type,
                collection,
                id_field=id_field,
            ),
        )

    return cls


def _handle_implements_specific_methods(
    cls: type,
    *specific_methods: SpecificMethod,
) -> type:
    attrs = _get_meta_attributes(cls)
    dto_type = attrs['dto']
    collection = attrs['collection']
    id_field = attrs['id_field']
    for method in specific_methods:
        setattr(
            cls,
            method.name,
            _substitute_specific_method(
                MethodDeps(collection=collection, id_field=id_field, dto_type=dto_type),
                method=method,
            ),
        )
    return cls
