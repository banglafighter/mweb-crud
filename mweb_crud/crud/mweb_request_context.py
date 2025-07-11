import re
from typing import Optional, Callable
from mw_common import DataUtil
from mweb import mweb_request
from mweb_crud.common import MWebCRUDException
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.data_transfer import MWebBaseDTO, MWebDTO, MWebIDDTO, MWebDatedDTO


class RequestContext:

    async def get_json_body(self, default=None):
        try:
            json_dict = await mweb_request.get_json()
            if json_dict is not None:
                return json_dict
            return default
        except Exception as e:
            raise MWebCRUDException(message=str(e))

    async def get_data(self, validator: MWebBaseDTO | MWebDTO | MWebIDDTO | MWebDatedDTO  = None, clean: bool = False, many: bool = False, before_validate: Optional[Callable[[dict], None]] = None, after_validate: Optional[Callable[[dict], None]] = None):
        wrapped_data = await self.get_json_body()
        data = DataUtil.dict_value(data=wrapped_data, key="data", default=None)

        if not data:
            raise MWebCRUDException(message=MWebCRUDConfig.INVALID_JSON_REQUEST_DATA_MSG)

        if not validator:
            return data

        if before_validate is not None and callable(before_validate):
            before_validate(data)

        errors = validator.validate(data=data, many=many)
        if errors and isinstance(errors, dict):
            raise MWebCRUDException(message=MWebCRUDConfig.DATA_VALIDATION_ERROR_MSG, details=errors)

        if clean:
            data = validator.clean_dict(data=data)

        if after_validate is not None and callable(after_validate):
            after_validate(data)

        return data

    async def get_form_data(self, default=None):
        try:
            form_data = await mweb_request.form
            if form_data is not None:
                return form_data
            return default
        except Exception as e:
            raise MWebCRUDException(message=str(e))

    async def get_uploaded_files(self, default=None):
        try:
            files = await mweb_request.files
            if files is not None:
                return files
            return default
        except Exception as e:
            raise MWebCRUDException(message=str(e))

    def get_header(self, name: str, default=None):
        return mweb_request.headers.get(name, default)

    def get_auth_header(self):
        header = self.get_header("Authorization")
        if not header:
            header = self.get_header("authorization")
        return header

    def extract_bearer_token(self):
        authorization_header = self.get_auth_header()
        if not authorization_header:
            return None
        group = re.match("^Bearer\\s+(.*)", authorization_header)
        if group:
            return group.group(1)
        return None

    def get_query_params(self, default=None):
        data = mweb_request.args
        if data:
            return data
        return default

    def get_query_param(self, key: str, default=None, type=None):
        data = self.get_query_params(default=None)
        if not data:
            return default
        if key in data:
            value = data.getlist(key, type)
            if len(value) == 1:
                return value[0]
            return value
        return default
