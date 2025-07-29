import enum
from marshmallow import ValidationError


def validate_enum_value(values: list, value: str, key: str, message: str = "Value should be any of "):
    if str(value) not in values:
        message += '(' + ', '.join(str(v) for v in values) + ')'
        raise ValidationError(message, key)


class BaseEnum(enum.Enum):

    @classmethod
    def values(cls) -> list:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def keys(cls) -> list:
        return list(map(lambda c: c.name, cls))

    @classmethod
    def to_map(cls) -> dict:
        data = {}
        for enum_type in cls:
            data[enum_type.name] = enum_type.value
        return data

    @classmethod
    def value_to_key(cls, value):
        for enum_type in cls:
            if enum_type.value == value:
                return enum_type.name
        return None

    def __str__(self):
        return self.value

    def is_mw_enum(self):
        return True