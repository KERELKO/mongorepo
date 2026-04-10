from dataclasses import asdict, is_dataclass

from mongorepo.exceptions import EntityIsNotDataclass
from mongorepo.types.collection_provider import CollectionProvider
from mongorepo.types.repository_config import RepositoryConfig
from mongorepo.utils.dataclass_converters import get_converter
from mongorepo.utils.mongorepo_dict import get_or_create_mongorepo_dict
from mongorepo.utils.type_hints import get_entity_type_hints, is_entity_field
from mongorepo.utils.validations import (
    validate_specific_method_input_parameters,
)

from ._substitute import _substitute_specific_method
from .methods import SpecificFieldMethod, SpecificMethod


def _handle_implement_specific_methods[T: type](
    cls: T, *specific_methods: SpecificMethod | SpecificFieldMethod, config: RepositoryConfig,
) -> T:
    __mongorepo__ = get_or_create_mongorepo_dict(
        cls, CollectionProvider(obj=cls, collection=config.collection), config,
    )
    if not config.to_document_converter and not config.to_entity_converter and not is_dataclass(
        config.entity_type,
    ):
        raise EntityIsNotDataclass(
            f"Provided entity type '{config.entity_type.__name__}' does not implement "
            "dataclass interface. For non dataclass entities provide converters explicitly, "
            "otherwise there is no way to convert entity to document and from document to entity.",
        )

    config.to_document_converter = config.to_document_converter or asdict
    config.to_entity_converter = config.to_entity_converter or get_converter(config.entity_type)

    entity_type_hints = get_entity_type_hints(config.entity_type)

    for method in specific_methods:
        validate_specific_method_input_parameters(method, config.entity_type)

        if hasattr(method, 'target_field'):
            target_field = method.target_field

            if is_entity_field(
                field_type := entity_type_hints[target_field.name], config.entity_type,
            ):
                target_field.field_type = field_type
                target_field.to_document_converter = config.to_document_converter
                target_field.to_entity_converter = config.to_entity_converter
                target_field.is_primitive = False
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
