from dataclasses import asdict

from mongorepo.types.collection_provider import CollectionProvider
from mongorepo.types.repository_config import RepositoryConfig
from mongorepo.utils.dataclass_converters import get_converter
from mongorepo.utils.field_factory import build_validated_field
from mongorepo.utils.mongorepo_dict import get_or_create_mongorepo_dict
from mongorepo.utils.type_hints import get_entity_type_hints
from mongorepo.utils.validations import validate_repository_config_converters

from ._substitute import _substitute_specific_method
from .methods import SpecificFieldMethod, SpecificMethod
from .validations import validate_specific_method_input_parameters


def _handle_implement_specific_methods[T: type](
    cls: T, *specific_methods: SpecificMethod | SpecificFieldMethod, config: RepositoryConfig,
) -> T:
    validate_repository_config_converters(config)
    __mongorepo__ = get_or_create_mongorepo_dict(
        cls, CollectionProvider(obj=cls, collection=config.collection), config,
    )

    config.to_document_converter = config.to_document_converter or asdict
    config.to_entity_converter = config.to_entity_converter or get_converter(config.entity_type)

    entity_type_hints = get_entity_type_hints(config.entity_type)

    for method in specific_methods:
        validate_specific_method_input_parameters(method, config.entity_type)

        if hasattr(method, 'target_field'):
            build_validated_field(
                method.target_field, entity_type_hints[method.target_field.name], config,
            )

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
