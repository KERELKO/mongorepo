from mongorepo import exceptions
from mongorepo._collections import COLLECTION_PROVIDER, CollectionProvider
from mongorepo.utils import _get_meta_attributes

from ._substitute import _substitute_specific_method
from .methods import SpecificMethod


def _handle_implements_specific_methods[T: type](cls: T, *specific_methods: SpecificMethod) -> T:
    attrs = _get_meta_attributes(cls)
    dto_type = attrs['dto']
    if not dto_type:
        raise exceptions.NoDTOTypeException
    collection = attrs['collection']
    id_field = attrs['id_field']

    if not hasattr(cls, COLLECTION_PROVIDER):
        setattr(cls, COLLECTION_PROVIDER, CollectionProvider(collection))

    for method in specific_methods:
        setattr(
            cls,
            method.name,
            _substitute_specific_method(
                cls,  # type: ignore
                method=method,
                dto_type=dto_type,
                id_field=id_field,
            ),
        )
    return cls
