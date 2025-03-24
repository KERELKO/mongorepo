from enum import StrEnum
from typing import Literal


class MethodAction(StrEnum):
    GET = 'get'
    GET_LIST = 'get_list'
    GET_ALL = 'get_all'
    UPDATE = 'update'
    ADD = 'add'
    ADD_BATCH = 'add_batch'
    DELETE = 'delete'

    INTEGER_INCREMENT = 'incr__'
    INTEGER_DECREMENT = 'decr__'

    LIST_APPEND = '__append'
    LIST_REMOVE = '__remove'
    LIST_POP = '__pop'
    LIST_FIELD_VALUES = '__list'

    def as_mongo_action(self) -> str:
        match self:
            case self.LIST_APPEND:
                return '$push'
            case self.LIST_REMOVE:
                return '$pull'
            case self.LIST_POP:
                return '$pop'
        return self.value


class ParameterEnum(StrEnum):
    FILTER = 'filters'
    OFFSET = 'offset'
    LIMIT = 'limit'
    DTO = 'dto'
    VALUE = 'value'
    WEIGHT = 'weight'
    FILTER_ALIAS = '__filter_alias'


LParameter = Literal[
    ParameterEnum.FILTER,
    ParameterEnum.OFFSET,
    ParameterEnum.LIMIT,
    ParameterEnum.DTO,
    ParameterEnum.VALUE,
    ParameterEnum.WEIGHT,
    ParameterEnum.FILTER_ALIAS,
]
