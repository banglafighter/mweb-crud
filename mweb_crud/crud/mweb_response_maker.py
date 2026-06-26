from mweb import MWebResponse
from ..data_transfer import MWebBaseDTO, MWebDatedDTO, MWebIDDTO, MWebDTO
from ..randr import MWebRESTResponseData, MWebRESTResponseStatus, MWebRESTResponseCode
from mweb_orm import MWebBaseModel, MWebIDModel, MWebDatedModel, MWebModel, Pagination


class ResponseMaker:

    @classmethod
    async def success(cls, content: str | dict | list = None, message: str = None, code: int = None, http_code: int = None, headers: dict = None):
        if not code:
            code = MWebRESTResponseCode.success

        response = MWebRESTResponseData(
            status=MWebRESTResponseStatus.success,
            code=code,
            message=message,
            httpCode=http_code,
        )

        if not message and isinstance(content, str):
            response.message = content
        else:
            response.data = content

        return await MWebResponse.json_response(content=response.to_json(), headers=headers, http_code=http_code)


    @classmethod
    async def success_from_model(cls, model: MWebModel | MWebBaseModel | list[MWebBaseModel] | MWebIDModel | MWebDatedModel | Pagination, transformer: MWebDTO | MWebBaseDTO | MWebDatedDTO | MWebIDDTO, message: str = None, code: int = None, http_code: int = None, headers: dict = None, as_transform: bool = False, as_dict: bool = False):
        if not code:
            code = MWebRESTResponseCode.success

        response = MWebRESTResponseData(
            status=MWebRESTResponseStatus.success,
            code=code,
            message=message,
            httpCode=http_code,
        )

        transformed_response = None
        if isinstance(model, Pagination):
            transformed_response = transformer.to_dict(model=model.items, many=True)
            response.set_pagination(pagination=model)
        elif isinstance(model, list):
            transformed_response = transformer.to_dict(model=model, many=True)
        else:
            transformed_response = transformer.to_dict(model=model)

        if as_transform:
            return transformed_response
        response.data = transformed_response
        content = response.to_dict()
        if as_dict:
            return content
        return await MWebResponse.make_response(content=content, headers=headers, http_code=http_code)

    @classmethod
    async def paginated(cls, paginated_model: Pagination, data: list, message: str = None, code: int = None, http_code: int = None, headers: dict = None, as_dict: bool = False):
        response = MWebRESTResponseData(
            status=MWebRESTResponseStatus.success,
            code=code,
            message=message,
            httpCode=http_code,
            data=data,
        )
        response.set_pagination(pagination=paginated_model)
        if as_dict:
            return response.to_dict()
        content = response.to_json()
        return await MWebResponse.json_response(content=content, headers=headers, http_code=http_code)



    @classmethod
    async def error(cls, message: str, details: dict = None, code: int = None, http_code: int = None, headers: dict = None, data: dict | list = None):
        if not code:
            code = MWebRESTResponseCode.error

        response = MWebRESTResponseData(
            status=MWebRESTResponseStatus.error,
            code=code,
            message=message,
            httpCode=http_code,
            data=data,
        )

        if details:
            response.set_error(errors=details)
        return await MWebResponse.json_response(content=response.to_json(), headers=headers, http_code=http_code)
