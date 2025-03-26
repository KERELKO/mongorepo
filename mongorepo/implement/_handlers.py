from mongorepo import exceptions
from mongorepo._base import CollectionProvider
from mongorepo._common import MongorepoDict
from mongorepo.utils import _get_meta_attributes

from ._substitute import _substitute_specific_method
from .methods import SpecificMethod


def _handle_implement_specific_methods[T: type](cls: T, *specific_methods: SpecificMethod) -> T:
    attrs = _get_meta_attributes(cls)
    dto_type = attrs['dto']
    if not dto_type:
        raise exceptions.NoDTOTypeException
    collection = attrs['collection']
    id_field = attrs['id_field']

    if hasattr(cls, '__mongorepo__'):
        __mongorepo__: MongorepoDict = getattr(cls, '__mongorepo__')  # noqa
    else:
        __mongorepo__ = MongorepoDict(
            collection_provider=CollectionProvider(obj=cls, collection=collection), methods={},
        )

    for method in specific_methods:
        implemented_method = _substitute_specific_method(
            cls,
            method=method,
            dto_type=dto_type,
            id_field=id_field,
        )
        __mongorepo__['methods'][method.name] = implemented_method  # type: ignore

        setattr(cls, method.name, __mongorepo__['methods'][method.name])

    setattr(cls, '__mongorepo__', __mongorepo__)
    return cls
