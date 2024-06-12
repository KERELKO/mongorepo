"""## !Package not implemented"""
from typing import Any, Callable, Type, TypeVar

from pymongo.collection import Collection

from mongorepo import exceptions
from mongorepo import DTO
from mongorepo.utils import _get_meta_attributes
from mongorepo._methods import METHOD_NAME__CALLABLE


def substitute_class_methods(target_cls: type, source_cls: type) -> type:
    attributes = _get_meta_attributes(target_cls)
    substitute: dict[str, str] | None = attributes['substitute']
    dto, collection = attributes['dto'], attributes['collection']

    if not substitute:
        raise exceptions.NoSubstituteException

    for mongo_method, cls_method in substitute.items():
        __substitute_method(
            method_name=mongo_method,
            target_cls=target_cls,
            source_cls=source_cls,
            cls_method=cls_method,
            dto=dto,
            collection=collection,
        )
    return target_cls


def __substitute_method(
    method_name: str,
    target_cls: type,
    source_cls: type,
    cls_method: str,
    dto: Type[DTO],
    collection: Collection,
) -> None:
    _method = METHOD_NAME__CALLABLE.get(method_name, None)
    if not _method:
        raise exceptions.InvalidMethodNameException(
            method_name,
            available_methods=tuple(METHOD_NAME__CALLABLE.keys()),
        )

    _cls_method: Callable | None = getattr(source_cls, cls_method, None)
    if not _cls_method:
        raise exceptions.InvalidMethodNameInSourceClassException(cls_method, source_cls)

    get_: Callable = _method(dto_type=dto, collection=collection)

    get_.__annotations__ = _cls_method.__annotations__
    get_.__name__ = _cls_method.__name__
    print(get_.__annotations__)

    replace_typevar_in_annotations(dto, get_)

    setattr(target_cls, cls_method, get_)


def replace_typevar_in_annotations(type_name: Any, func: Callable) -> None:
    for hint, val in func.__annotations__.items():
        if isinstance(val, TypeVar):
            func.__annotations__[hint] = type_name
