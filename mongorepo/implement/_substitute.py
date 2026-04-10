import inspect
from dataclasses import asdict
from typing import Any, Callable

from mongorepo import exceptions
from mongorepo.types import Dataclass, RepositoryConfig
from mongorepo.utils.dataclass_converters import get_converter
from mongorepo.utils.type_hints import get_function_default_values

from .enums import MethodAction
from .enums import ParameterEnum as MongorepoParameter
from .method_mapper_utils import (
    implement_mapper,
    initialize_callable_mongorepo_method,
)
from .methods import Method, SpecificFieldMethod, SpecificMethod


def _substitute_specific_method(
    cls,
    method: SpecificMethod | SpecificFieldMethod,
    entity_type: type[Dataclass],
    config: RepositoryConfig,
    **kwargs,
) -> Callable:
    is_async = inspect.iscoroutinefunction(method.source)

    if hasattr(method, 'target_field'):
        target_field = method.target_field  # type: ignore[attr-defined]
    else:
        target_field = None

    if hasattr(method, 'integer_weight'):
        integer_weight = method.integer_weight  # type: ignore[attr-defined]
    else:
        integer_weight = None

    mapped_method = implement_mapper(method)
    to_document_converter = config.to_document_converter or asdict
    to_entity_converter = config.to_entity_converter or get_converter(config.entity_type)

    callable_mongorepo_method = initialize_callable_mongorepo_method(
        mongorepo_method=mapped_method,
        entity_type=entity_type,
        owner=cls,
        target_field=target_field,
        integer_weight=integer_weight,
        to_entity_converter=to_entity_converter,
        to_document_converter=to_document_converter,
        modifiers=method.modifiers,
    )

    def func(self, *args, **kwargs) -> Any:
        required_params = _manage_custom_params(
            Method(source=method.source, **method.params), *args, **kwargs,
        )
        return callable_mongorepo_method(**required_params)

    async def async_func(self, *args, **kwargs) -> Any:
        required_params = _manage_custom_params(
            Method(source=method.source, **method.params), *args, **kwargs,
        )
        return await callable_mongorepo_method(**required_params)

    if method.action == MethodAction.GET_ALL and is_async is True:
        new_method = func
    else:
        new_method = async_func if is_async else func

    new_method.__annotations__ = method.source.__annotations__
    new_method.__name__ = method.name

    return new_method


def _manage_custom_params(
    method: Method,
    *args,
    **kwargs,
) -> dict[str, Any]:
    defaults = get_function_default_values(method.source)
    result: dict[str, Any] = {}
    filters: dict[str, Any] = {}
    source_params_map: dict[str, Any] = {}
    aliases: dict[str, Any] = method.params.get(MongorepoParameter.FILTER_ALIAS, {})  # type: ignore
    i = 0

    # Iterate over all names of the method's arguments
    for source_param in method.get_source_params().keys():

        # Parameter was passed as positional argument
        if len(args) > i:
            source_params_map[source_param] = args[i]
            i += 1
            continue

        # Parameter was passed as keyword argument ?
        elif source_param in kwargs:
            source_params_map[source_param] = kwargs[source_param]

        # If parameter was not passed check for defaults
        elif defaults.get(source_param, None):
            source_params_map[source_param] = defaults[source_param]

        # Missing parameter
        else:
            raise exceptions.MongorepoException(
                message=f'Cannot find value for {source_param} parameter, '
                f'{method.name}() parameters: {method.params}',
            )

    for key, value in source_params_map.items():
        # Check for filter
        if method.params.get(key, None) == MongorepoParameter.FILTER:
            filters[key] = value
        # Check alias
        elif (dto_field := aliases.get(key, None)) is not None:
            filters[dto_field] = value
        else:
            result[method.params[key]] = value

    result.update(filters)
    return result
