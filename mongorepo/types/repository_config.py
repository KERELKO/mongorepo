from dataclasses import dataclass
from typing import Any, Callable

from .method_access import MethodAccess


@dataclass(slots=True)
class RepositoryConfig[CollectionType]:
    """Configuration data class for a Mongorepo repository.

    Defines the foundational settings required to map a Python entity
    (typically a dataclass) to a MongoDB collection, including access
    controls and custom serialization/deserialization logic.

    """

    entity_type: type
    """The Python type or class of the entity that this repository manages."""

    collection: CollectionType | None = None
    """The MongoDB collection instance used by the repository for database
    operations."""

    method_access: MethodAccess | None = None
    """Configuration defining access control and permissions for repository
    methods."""

    to_document_converter: Callable[[Any], dict] | None = None
    """Custom callable to serialize a Python entity into a MongoDB document
    (dict).

    If the target entity contains nested entities, this converter is applied
    to them as well. By default, Mongorepo expects dataclass-based entities
    and will fall back to :func:`dataclasses.asdict` if no custom converter is provided.

    """

    to_entity_converter: Callable[[dict, type], Any] | None = None
    """Custom callable to deserialize a MongoDB document (dict) into the target
    entity.

    By default, Mongorepo utilizes its internal entity converter
    (see :func:`mongorepo.utils.dataclass_converters.get_converter`), which seamlessly
    handles instantiation for both top-level and nested entities.

    """
