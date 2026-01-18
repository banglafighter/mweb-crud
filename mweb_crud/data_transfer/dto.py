import enum
import typing
from marshmallow import fields
from mw_common import DataCastType, MwConverter
from mweb import FileStorage
from mweb_crud.data_transfer.df_helper import validate_enum_value, BaseEnum


class ExtendedFields:
    xlImport: bool = True
    xlExport: bool = True


class String(fields.String, ExtendedFields):
    des_cast: bool = False  # Deserialize casting

    def __init__(self, *args, xl_import=False, xl_export=False, des_cast=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.xlImport = xl_import
        self.xlExport = xl_export
        self.des_cast = des_cast

    def _deserialize(self, value, attr, data, **kwargs) -> str:
        if self.des_cast:
            value = str(value)
        return super()._deserialize(value, attr, data, **kwargs)


class Integer(fields.Integer, ExtendedFields):
    def __init__(self, *args, xl_import=False, xl_export=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.xlImport = xl_import
        self.xlExport = xl_export


class UUID(fields.UUID):
    pass


class Float(fields.Float, ExtendedFields):
    def __init__(self, *args, xl_import=False, xl_export=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.xlImport = xl_import
        self.xlExport = xl_export


class Decimal(fields.Decimal):
    pass


class Boolean(fields.Boolean, ExtendedFields):
    def __init__(self, *args, xl_import=False, xl_export=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.xlImport = xl_import
        self.xlExport = xl_export


class DateTime(fields.DateTime, ExtendedFields):
    def __init__(self, *args, xl_import=False, xl_export=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.xlImport = xl_import
        self.xlExport = xl_export


class Time(fields.Time):
    pass


class Date(fields.Date, ExtendedFields):
    def __init__(self, *args, xl_import=False, xl_export=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.xlImport = xl_import
        self.xlExport = xl_export


class Dict(fields.Dict):
    pass


class Url(fields.Url):
    pass


class Email(fields.Email, ExtendedFields):
    def __init__(self, *args, xl_import=False, xl_export=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.xlImport = xl_import
        self.xlExport = xl_export


class List(fields.List):
    pass


class Nested(fields.Nested):
    pass


class Enum(fields.String, ExtendedFields):
    enumType: BaseEnum
    cast_type: DataCastType | None = None

    def __init__(self, enum_type, *args, cast_type: DataCastType | None = None, xl_import=False, xl_export=False,
                 **kwargs):
        self.cast_type = cast_type
        self.enumType = enum_type
        super(Enum, self).__init__(*args, **kwargs)
        self.xlImport = xl_import
        self.xlExport = xl_export

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, enum.Enum):
            return value.value
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if hasattr(self.enumType, 'is_mw_enum'):
            validate_enum_value(self.enumType.values(), data[attr], attr)
        if self.cast_type is not None:
            value = MwConverter.dynamic_cast(value, self.cast_type)
        return value


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


class CustomNestedField(fields.Nested):

    def _deserialize(self, value, attr, data, partial=None, **kwargs):
        return value
