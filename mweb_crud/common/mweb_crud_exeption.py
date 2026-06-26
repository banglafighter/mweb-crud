from mw_common import MwException
from mweb import MWebResponse
from ..randr import MWebRESTResponseData, MWebRESTResponse, MWebRESTResponseStatus, MWebRESTResponseCode


class MWebCRUDException(MwException):
    response_data: MWebRESTResponseData = None

    def __init__(self, message=None, details: dict = None, error_code: int = None, http_code: int = None):
        super().__init__(message=message)

        if not error_code:
            error_code = MWebRESTResponseCode.error

        self.response_data = MWebRESTResponseData(
            status=MWebRESTResponseStatus.error,
            message=message,
            code=error_code,
            httpCode=http_code,
        )
        self.response_data.set_error(errors=details)

    async def handle_exception(self, exception: MwException):
        response = MWebRESTResponse.unexpected_error()

        if isinstance(exception, MWebCRUDException) and exception.response_data:
            response = exception.response_data

        return await MWebResponse.json_response(content=response.to_dict(), http_code=response.httpCode)
