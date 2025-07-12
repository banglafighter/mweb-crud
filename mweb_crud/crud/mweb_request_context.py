import re
from typing import Optional, Callable, Literal
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

    async def get_data(self, validator: MWebBaseDTO | MWebDTO | MWebIDDTO | MWebDatedDTO  = None, clean: bool = False, many: bool = False, read_from: Literal["json", "form"] = "json", before_validate: Optional[Callable[[dict], None]] = None, after_validate: Optional[Callable[[dict], None]] = None):

        data: dict | None = None
        if read_from == "json":
            wrapped_data = await self.get_json_body()
            data = DataUtil.dict_value(data=wrapped_data, key="data", default=None)
        elif read_from == "form":
            data = await self.form_and_file_to_dict()

        if data is None:
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

    async def form_data(self, default=None):
        try:
            form_data = await mweb_request.form
            if form_data is not None:
                return form_data
            return default
        except Exception as e:
            raise MWebCRUDException(message=str(e))

    def _convert_form_value(self, value):
        if value in ("null", "None", ""):
            return None
        return value

    def _convert_form_to_dict(self, form_data, default=None):
        if form_data is None:
            return default

        requested_data = form_data.to_dict(flat=False)
        response = {}
        for data in requested_data:
            if len(requested_data[data]) == 1:
                response[data] = self._convert_form_value(requested_data[data][0])
            else:
                response[data] = self._convert_form_value(requested_data[data])

        return response

    async def form_to_dict(self, default=None):
        form_data = await self.form_data()
        return self._convert_form_to_dict(form_data, default)

    async def uploaded_files(self, default=None):
        try:
            files = await mweb_request.files
            if files is not None:
                return files
            return default
        except Exception as e:
            raise MWebCRUDException(message=str(e))

    async def uploaded_file_to_dict(self, default=None):
        files_data = await self.uploaded_files()
        return self._convert_form_to_dict(files_data, default)

    async def form_and_file_to_dict(self, default=None):
        form_data = await self.form_to_dict(default={})
        file_data = await self.uploaded_file_to_dict(default={})
        form_data.update(file_data)
        if form_data:
            return form_data
        return default

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
