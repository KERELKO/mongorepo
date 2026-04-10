from typing import get_type_hints

from mongorepo.implement._types import ParameterEnum
from mongorepo.implement.exceptions import FieldDoesNotExist
from mongorepo.implement.methods import SpecificFieldMethod, SpecificMethod
from mongorepo.utils.type_hints import field_exists


def validate_specific_method_input_parameters(
    specific_method: SpecificMethod | SpecificFieldMethod, entity_type: type,
):
    for param_name, value in specific_method.params.items():
        # Validate name of field passed as filter
        if value == ParameterEnum.FILTER.value and field_exists(param_name, entity_type) is False:
            raise FieldDoesNotExist(
                param_name,
                correct_fields=list(get_type_hints(entity_type).keys()),
                entity=entity_type.__name__,
            )
        # Validate name of field passed as filter alias
        elif param_name == ParameterEnum.FILTER_ALIAS.value:
            for field in value.values():  # type: ignore[union-attr]
                if field_exists(field, entity_type) is False:
                    raise FieldDoesNotExist(
                        field,
                        correct_fields=list(get_type_hints(entity_type).keys()),
                        entity=entity_type.__name__,
                    )
