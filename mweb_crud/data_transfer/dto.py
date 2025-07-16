import enum
import typing
from marshmallow import fields
from mweb import FileStorage
from mweb_crud.data_transfer.df_helper import validate_enum_value, BaseEnum


class String(fields.String):
    pass


class Integer(fields.Integer):
    pass


class Float(fields.Float):
    pass


class Decimal(fields.Decimal):
    pass


class Boolean(fields.Boolean):
    pass


class DateTime(fields.DateTime):
    pass


class Time(fields.Time):
    pass


class Date(fields.Date):
    pass


class Dict(fields.Dict):
    pass


class Url(fields.Url):
    pass


class Email(fields.Email):
    pass


class List(fields.List):
    pass


class Nested(fields.Nested):
    pass


class Enum(fields.String):
    enumType: BaseEnum

    def __init__(self, enumType, *args, **kwargs):
        self.enumType = enumType
        super(Enum, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, enum.Enum):
            return value.value
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if hasattr(self.enumType, 'is_mw_enum'):
            validate_enum_value(self.enumType.values(), data[attr], attr)
        name = self.enumType.value_to_key(data[attr])
        return name

class File(fields.String):
    max_size_kb: int = None
    allowed_extensions: list = None
    is_multiple: bool = False
    is_string_name: bool = False
    is_uploaded: bool = False
    save_prefix: str = None

    default_error_messages = {
        "invalid": "Not a valid file."
    }

    def set_max_size_kb(self, size: int) -> "File":
        self.max_size_kb = size
        return self

    def set_allowed_extension(self, extension: list) -> "File":
        self.allowed_extensions = extension
        return self

    def allow_multiple(self) -> "File":
        self.is_multiple = True
        return self

    def allow_string_name(self) -> "File":
        self.is_string_name = True
        return self

    def set_save_prefix(self, prefix: str) -> "File":
        self.save_prefix = prefix
        return self

    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        if self.is_multiple and isinstance(value, list):
            for file in value:
                if not isinstance(file, FileStorage) and not self.is_string_name:
                    raise self.make_error("invalid")
            return value

        if not isinstance(value, FileStorage) and not self.is_string_name and not self.is_uploaded:
            raise self.make_error("invalid")
        return value
