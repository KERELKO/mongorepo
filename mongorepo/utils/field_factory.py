from mongorepo.types.field import Field
from mongorepo.types.repository_config import RepositoryConfig
from mongorepo.utils.type_hints import is_entity_field


def build_validated_field(
    existing_field: Field, target_field_type: type, repository_config: RepositoryConfig,
) -> None:
    """Rebuilds field based on config information and validates it."""
    if not existing_field.field_type:
        existing_field.field_type = target_field_type

    if is_entity_field(target_field_type, repository_config.entity_type):
        if not existing_field.to_document_converter:
            existing_field.to_document_converter = repository_config.to_document_converter
        if not existing_field.to_entity_converter:
            existing_field.to_entity_converter = repository_config.to_entity_converter
        existing_field.is_primitive = False
    else:
        existing_field.is_primitive = True
