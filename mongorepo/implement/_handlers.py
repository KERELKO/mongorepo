from mongorepo.collection_provider import CollectionProvider
from mongorepo.implement._utils import validate_input_parameters
from mongorepo.types import RepositoryConfig
from mongorepo.utils.mongorepo_dict import get_or_create_mongorepo_dict
from mongorepo.utils.type_hints import get_entity_type_hints, is_entity_field

from ._substitute import _substitute_specific_method
from .methods import SpecificFieldMethod, SpecificMethod


def _handle_implement_specific_methods[T: type](
    cls: T, *specific_methods: SpecificMethod | SpecificFieldMethod, config: RepositoryConfig,
) -> T:
    __mongorepo__ = get_or_create_mongorepo_dict(
        cls, CollectionProvider(obj=cls, collection=config.collection), config,
    )

    entity_type_hints = get_entity_type_hints(config.entity_type)

    for method in specific_methods:
        validate_input_parameters(method, config.entity_type)

        if hasattr(method, 'target_field'):
            target_field = method.target_field

            if is_entity_field(
                field_type := entity_type_hints[target_field.name], config.entity_type,
            ):
                target_field.is_primitive = False
                target_field.field_type = target_field.field_type or field_type
                target_field.to_document_converter = (
                    target_field.to_document_converter or config.to_document_converter
                )
                target_field.to_entity_converter = (
                    target_field.to_entity_converter or config.to_entity_converter
                )
            else:
                target_field.is_primitive = True

        implemented_method = _substitute_specific_method(
            cls,
            method=method,
            entity_type=config.entity_type,
            config=config,
        )
        __mongorepo__['methods'][method.name] = implemented_method  # type: ignore

        setattr(cls, method.name, __mongorepo__['methods'][method.name])

    setattr(cls, '__mongorepo__', __mongorepo__)
    return cls
