from mongorepo.exceptions import MongorepoException


class FieldDoesNotExist(MongorepoException):
    def __init__(self, field: str, correct_fields: list[str], entity: str):
        self.field = field
        self.correct_fields = correct_fields
        self.entity = entity

    def __str__(self) -> str:
        return f'{self.entity} has no field named "{self.field}". Actual fields: {self.correct_fields}'
