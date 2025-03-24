import inspect
from typing import Any, Callable

from mongorepo import exceptions
from mongorepo._base import Dataclass
from mongorepo.utils import _get_defaults

from ._types import MethodAction
from ._types import ParameterEnum as MongorepoParameter
from ._utils import implement_mapper, initialize_callable_mongorepo_method
from .methods import Method, SpecificFieldMethod, SpecificMethod


def _substitute_specific_method(
    cls,
    method: SpecificMethod | SpecificFieldMethod,
    dto_type: type[Dataclass],
    id_field: str | None = None,
    field_name: str | None = None,
    integer_weight: int | None = None,
    **kwargs,
) -> Callable:
    is_async = inspect.iscoroutinefunction(method.source)

    if hasattr(method, 'field_name'):
        field_name = method.field_name  # type: ignore

    if hasattr(method, 'integer_weight'):
        integer_weight = method.integer_weight  # type: ignore

    mapped_method = implement_mapper(method)
    callable_mongorepo_method = initialize_callable_mongorepo_method(
        mongorepo_method=mapped_method,
        dto_type=dto_type,
        owner=cls,
        id_field=id_field,
        field_name=field_name,
        integer_weight=integer_weight,
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
    defaults = _get_defaults(method.source)
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
        if method.params.get(key, None) == MongorepoParameter.FILTER:
            filters[key] = value
        elif (dto_field := aliases.get(key, None)) is not None:
            filters[dto_field] = value
        else:
            result[method.params[key]] = value

    result.update(filters)
    return result
