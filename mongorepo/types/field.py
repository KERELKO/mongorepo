from typing import Any

from mongorepo.exceptions import MongorepoException

from .base import ToDocumentConverter, ToEntityConverter


class Field[T]:
    """Class that represents a field of an entity."""

    __slots__ = (
        'name', '_is_primitive', 'field_type', 'to_document_converter', 'to_entity_converter',
    )

    def __init__(
        self,
        name: str,
        field_type: type | None = None,
        is_primitive: bool = True,
        to_document_converter: ToDocumentConverter[T] | None = None,
        to_entity_converter: ToEntityConverter[T] | None = None,
    ) -> None:
        self.name = name
        self.field_type = field_type
        self.to_document_converter = to_document_converter
        self.to_entity_converter = to_entity_converter
        self._is_primitive = is_primitive
        self._validate()

    def to_document(self, value: Any) -> Any:
        return value if self._is_primitive else self.to_document_converter(
            value,
        )  # type: ignore[misc]

    def to_value(self, doc: Any) -> Any:
        return doc if self._is_primitive else self.to_entity_converter(
            doc, self.field_type,  # type: ignore[misc, arg-type]
        )

    def _validate(self) -> None:
        if self._is_primitive is False and (
            self.to_document_converter is None or self.to_entity_converter is None
        ):
            raise MongorepoException(
                f"Cannot handle non-primitive entity field '{self.name}' "
                f"of type '{self.field_type}' without converters. Please provide "
                f"to_document_converter and to_entity_converter for field '{self.name}'",
            )
        if not self._is_primitive and not self.field_type:
            raise MongorepoException(
                f"Cannot identify type of the non-primitive entity field '{self.name}'. "
                f"Please provide type for '{self.name}' field",
            )

    @property
    def is_primitive(self) -> bool:
        return self._is_primitive

    @is_primitive.setter
    def is_primitive(self, value: bool):
        self._is_primitive = value
        self._validate()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(name={self.name}, field_type={self.field_type}, "
            f"is_primitive={self._is_primitive}, "
            f"to_document_converter={self.to_document_converter}, "
            f"to_entity_converter={self.to_entity_converter})"
        )
