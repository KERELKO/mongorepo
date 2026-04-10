from dataclasses import is_dataclass

from mongorepo.exceptions import EntityIsNotDataclass
from mongorepo.types.repository_config import RepositoryConfig


def validate_repository_config_converters(config: RepositoryConfig):
    if not config.to_document_converter and not config.to_entity_converter and not is_dataclass(
        config.entity_type,
    ):
        raise EntityIsNotDataclass(
            f"Provided entity type '{config.entity_type.__name__}' does not implement "
            "dataclass interface. For non dataclass entities provide converters explicitly, "
            "otherwise there is no way to convert entity to document and from document to entity.",
        )
