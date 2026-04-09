from typing import Any

from mongorepo.exceptions import MongorepoException
from mongorepo.types import ToDocumentConverter, ToEntityConverter


class Field[T]:
    """Class that represents a field of an entity."""

    __slots__ = (
        'name', 'is_primitive', 'field_type', 'to_document_converter', 'to_entity_converter',
    )

    def __init__(
        self,
        name: str,
        field_type: type | None = None,
        is_primitive: bool = True,
        to_document_converter: ToDocumentConverter[T] | None = None,
        to_entity_converter: ToEntityConverter[T] | None = None,
    ):
        self.name = name
        if is_primitive is False and (
            to_document_converter is None or to_entity_converter is None
        ):
            raise MongorepoException(
                f"Cannot handle non-primitive entity field '{name}' of type '{field_type}' "
                "without converters. "
                f"Please provide to_document_converter and to_entity_converter for field '{name}'",
            )
        if not is_primitive and not field_type:
            raise MongorepoException(
                f"Cannot identify type of the non-primitive entity field '{name}'. "
                f"Please provide type for '{name}' field",
            )
        self.field_type = field_type
        self.to_document_converter = to_document_converter
        self.to_entity_converter = to_entity_converter
        self.is_primitive = is_primitive

    def to_document(self, value: Any) -> Any:
        return value if self.is_primitive else self.to_document_converter(
            value,
        )  # type: ignore[misc]

    def to_value(self, doc: Any) -> Any:
        return doc if self.is_primitive else self.to_entity_converter(
            doc, self.field_type,  # type: ignore[misc, arg-type]
        )
