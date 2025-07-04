from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.ext.marshmallow.field_converter import FieldConverterMixin
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.common.mweb_crud_const import SwaggerCommon, SwaggerDataType, SwaggerDefinitionType
from mweb_crud.data_transfer import dto
from mweb_crud.swagger.mweb_swagger_data import SwaggerData
from mweb_crud.swagger.mweb_swagger_schema import MWebSwaggerSchema


class MWebSwaggerGenerator:
    _swagger_api_spec: APISpec = None

    def __init__(self):
        self.init_api_spec()

    def init_api_spec(self):
        FieldConverterMixin.field_mapping[dto.File] = ("string", "binary")
        self._swagger_api_spec = APISpec(
            title=MWebCRUDConfig.SWAGGER_TITLE,
            version=MWebCRUDConfig.SWAGGER_APP_VERSION,
            openapi_version="3.0.2",
            plugins=[MarshmallowPlugin()]
        )
        self._init_mweb_schema()

    def process_action_definitions(self, action_definitions: list):
        for definition in action_definitions:
            self.process(definition)

    def process(self, definition: SwaggerData):
        definition.init_schema_key()
        self._entry_spec(definition)

    def get_swagger_spec(self):
        specification = {}
        if self._swagger_api_spec:
            specification = self._swagger_api_spec.to_dict()
            specification = self._enable_api_auth(specification)
        return specification

    def _init_mweb_schema(self):
        self._add_component_schema(SwaggerCommon.MESSAGE_RESPONSE, MWebSwaggerSchema.mweb_api_message_response_schema())
        self._add_component_schema(SwaggerCommon.ERROR_DETAILS_RESPONSE, MWebSwaggerSchema.mweb_api_error_response_schema())

    def _add_component_schema(self, key: str, data):
        if key not in self._swagger_api_spec.components.schemas:
            self._swagger_api_spec.components.schema(key, schema=data)

    def _entry_spec(self, definition: SwaggerData):
        if definition.url:
            self._swagger_api_spec.path(
                path=definition.url,
                parameters=self._get_query_and_url_parameters(definition),
                operations=self._get_operations(definition)
            )

    def _get_query_and_url_parameters(self, definition: SwaggerData):
        parameters = []
        self._process_get_request_parameters(definition.query_params, parameters, MWebSwaggerSchema.IN_QUERY)
        self._process_get_request_parameters(definition.url_params, parameters, MWebSwaggerSchema.IN_PATH)

        if parameters:
            return parameters
        return None

    def _process_get_request_parameters(self, params, parameters, place):
        if params:
            for query in params:
                if isinstance(query, tuple) and len(query) != 0:
                    name = self._get_tuple_value(query, 0)
                    data_type = self._get_tuple_value(query, 1, SwaggerDataType.string)
                    is_required = self._get_tuple_value(query, 2, False)
                    parameters.append(MWebSwaggerSchema.get_url_param_schema(place, name, data_type, is_required))
        return parameters

    def _get_tuple_value(self, data: tuple, index: int, default=None):
        try:
            return data[index]
        except:
            return default

    def _get_operations(self, definition: SwaggerData):
        operations = {}
        for method in definition.methods:
            request_body = self._process_and_add_request_schema(definition)
            responses = self._process_and_add_response_schema(definition)
            method = method.lower()
            operations[method] = {}
            if request_body:
                operations[method]["requestBody"] = request_body
            if responses:
                operations[method]["responses"] = responses
            if definition.tags:
                operations[method]["tags"] = definition.tags
        if operations:
            return operations
        return None

    def _process_and_add_request_schema(self, definition: SwaggerData):
        request_schema = None
        many = False
        if definition.request_obj:
            request_schema = definition.request_obj
            if definition.def_type != SwaggerDefinitionType.FORM_DATA and definition.def_type != SwaggerDefinitionType.FILE_UPLOAD:
                request_schema = MWebSwaggerSchema.mweb_api_data_schema(definition.request_obj)

        elif definition.request_list:
            many = True
            request_schema = MWebSwaggerSchema.mweb_api_data_schema(definition.request_list, many=many)

        if request_schema:
            self._add_component_schema(definition.request_schema_key, request_schema)
            return MWebSwaggerSchema.get_request_body(definition, many=many)
        return None

    def _process_and_add_response_schema(self, definition: SwaggerData):
        response_schema = None
        many = False
        if definition.response_obj:
            response_schema = definition.response_obj
        elif definition.response_list:
            many = True
            response_schema = definition.response_list

        if definition.def_type == SwaggerDefinitionType.PAGINATION:
            response_schema = MWebSwaggerSchema.mweb_api_paginate_response_schema(response_schema)
        else:
            response_schema = MWebSwaggerSchema.mweb_api_response_data_schema(response_schema, many=many)

        if response_schema:
            self._add_component_schema(definition.response_schema_key, response_schema)
            return MWebSwaggerSchema.get_response_body(definition, many=many)
        return None

    def _enable_api_auth(self, definition: dict):
        if MWebCRUDConfig.ENABLED_JWT_AUTH:
            if definition and isinstance(definition, dict):
                definition['security'] = [{"bearerAuth": []}]
                if "components" not in definition:
                    definition["components"] = {}
                definition["components"]["securitySchemes"] = {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
        return definition
