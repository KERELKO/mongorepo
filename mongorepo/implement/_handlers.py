from mongorepo.collection_provider import CollectionProvider
from mongorepo.types import RepositoryConfig
from mongorepo.utils.mongorepo_dict import get_or_create_mongorepo_dict

from ._substitute import _substitute_specific_method
from .methods import SpecificMethod


def _handle_implement_specific_methods[T: type](
    cls: T, *specific_methods: SpecificMethod, config: RepositoryConfig,
) -> T:
    __mongorepo__ = get_or_create_mongorepo_dict(
        cls, CollectionProvider(obj=cls, collection=config.collection), config,
    )

    for method in specific_methods:
        implemented_method = _substitute_specific_method(
            cls,
            method=method,
            entity_type=config.entity_type,
            id_field=config.id_field,
        )
        __mongorepo__['methods'][method.name] = implemented_method  # type: ignore

        setattr(cls, method.name, __mongorepo__['methods'][method.name])

    setattr(cls, '__mongorepo__', __mongorepo__)
    return cls
