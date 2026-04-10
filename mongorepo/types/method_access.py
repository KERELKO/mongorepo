from enum import Enum


class MethodAccess(int, Enum):
    """Use to indicate method access in a repository."""
    PUBLIC = 0
    PROTECTED = 1
    PRIVATE = 2


def get_method_access_prefix(access: MethodAccess | None, cls: type | None = None) -> str:
    """
    Returns string prefix according to MethodAccess value,
    * it can be `'_'`, `'__'`, `_{cls.__name__}__` or `''`
    """
    match access:
        case MethodAccess.PRIVATE:
            prefix = f'_{cls.__name__}__' if cls else '__'
        case MethodAccess.PROTECTED:
            prefix = '_'
        case MethodAccess.PUBLIC | None:
            prefix = ''
    return prefix
