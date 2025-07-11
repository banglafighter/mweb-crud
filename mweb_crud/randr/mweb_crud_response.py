from dataclasses import dataclass
from mw_common import SDLize
from .mweb_crud_randr_const import MWebRESTResponseCode, MWebRESTResponseStatus
from mweb_orm.common import Pagination


@dataclass(kw_only=True)
class MWebRESTResponseData(SDLize):
    status: str = None
    code: int = None
    httpCode: int = None
    message: str = None
    data: dict | list = None
    error: dict = None
    pagination: Pagination = None

    def set_pagination(self, pagination: Pagination, data: list = None):
        if data:
            self.data = data
        pagination.items = None
        self.pagination = pagination
        return self

    def set_error(self, errors: dict):
        if errors is None:
            return self

        message_dict: dict = {}
        for field_name in errors:
            error_text: str = ""
            messages = errors[field_name]
            if messages and isinstance(messages, list):
                for text in errors[field_name]:
                    error_text += str(text) + " "
            else:
                error_text = messages
            message_dict[field_name] = error_text.rstrip()
        self.error = message_dict
        return self


class MWebRESTResponse:
    @staticmethod
    def unexpected_error(message: str = None) -> MWebRESTResponseData:
        if not message:
            message = "Unexpected Error"
        return MWebRESTResponse.error(message=message)

    @staticmethod
    def error(message: str, error: dict = None, code: int = None, http_code: int = None) -> MWebRESTResponseData:
        if not code:
            code = MWebRESTResponseCode.error

        response = MWebRESTResponseData(
            code=code,
            error=error,
            httpCode=http_code,
            status=MWebRESTResponseStatus.error,
            message=message,
        )
        return response
