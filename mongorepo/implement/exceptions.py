from mongorepo.exceptions import MongorepoException


class FieldDoesNotExist(MongorepoException):
    def __init__(self, field: str, correct_fields: list[str], dto: str):
        self.field = field
        self.correct_fields = correct_fields
        self.dto = dto

    def __str__(self) -> str:
        return f'{self.dto} has no field named "{self.field}". Actual fields: {self.correct_fields}'
