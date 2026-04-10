from dataclasses import dataclass
from typing import Any, Callable

from mongorepo.types.method_access import MethodAccess


@dataclass(slots=True)
class RepositoryConfig[CollectionType]:
    """Config for Mongorepo repository."""
    entity_type: type
    """Type of the entity on which repository will operate."""
    collection: CollectionType | None = None
    """Collection which mongorepo will use to access DB."""
    method_access: MethodAccess | None = None
    """Access to mongorepo methods."""

    to_document_converter: Callable[[Any], dict] | None = None
    to_entity_converter: Callable[[dict, type], Any] | None = None
