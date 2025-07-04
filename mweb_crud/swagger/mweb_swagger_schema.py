from marshmallow import Schema, fields
from mweb_crud.common.mweb_crud_const import SwaggerCommon
from mweb_crud.swagger.mweb_swagger_data import SwaggerData


class MWebSwaggerSchema:
    IN_PATH = "path"
    IN_QUERY = "query"
    OBJ = "object"
    ARRAY = "array"
    JWT_SCHEME = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}

    @staticmethod
    def get_url_param_schema(place, name, data_type, required=False):
        return {
            "name": name,
            "in": place,
            "schema": {
                "type": data_type
            },
            "required": required
        }

    @staticmethod
    def get_component_schemas_link(name):
        return "#/components/schemas/" + name

    @staticmethod
    def get_schema_type(many):
        schema_type = None
        if many:
            schema_type = MWebSwaggerSchema.ARRAY
        return schema_type

    @staticmethod
    def get_schema_def_and_ref(ref, schema_type=None):
        schema = {"type": schema_type}
        if schema_type == MWebSwaggerSchema.ARRAY:
            schema["items"] = {
                "$ref": MWebSwaggerSchema.get_component_schemas_link(ref)
            }
            return schema
        return {"$ref": MWebSwaggerSchema.get_component_schemas_link(ref)}

    @staticmethod
    def get_request_body(definition: SwaggerData, many=False):
        schema_type = MWebSwaggerSchema.get_schema_type(many)
        return {
            "required": True,
            "content": {
                definition.request_content_type: {
                    "schema": MWebSwaggerSchema.get_schema_def_and_ref(definition.request_schema_key, schema_type)
                }
            }
        }

    @staticmethod
    def get_response_body(definition: SwaggerData, many=False):
        schema_type = MWebSwaggerSchema.get_schema_type(many)
        schema = MWebSwaggerSchema.get_schema_def_and_ref(definition.response_schema_key, schema_type)

        any_of_response = {"anyOf": []}
        if definition.response_obj or definition.response_list:
            any_of_response["anyOf"].append(MWebSwaggerSchema.get_schema_def_and_ref(definition.response_schema_key))
        if definition.mweb_message_response:
            any_of_response["anyOf"].append(MWebSwaggerSchema.get_schema_def_and_ref(SwaggerCommon.MESSAGE_RESPONSE))
        if definition.mweb_error_details_response:
            any_of_response["anyOf"].append(MWebSwaggerSchema.get_schema_def_and_ref(SwaggerCommon.ERROR_DETAILS_RESPONSE))
        schema = any_of_response

        return {
            definition.http_response_code: {
                "content": {
                    definition.response_content_type: {
                        "schema": schema
                    }
                }
            }
        }

    @staticmethod
    def mweb_api_data_schema(data, many=False):
        return Schema.from_dict({
            "data": fields.Nested(data, many=many)
        })

    @staticmethod
    def mweb_api_response_base_schema_map():
        return {
            "status": fields.String(),
            "code": fields.String(),
        }

    @staticmethod
    def mweb_api_response_data_schema(data, many=False, response_map=False):
        schema_map = MWebSwaggerSchema.mweb_api_response_base_schema_map()
        if data:
            schema_map["data"] = fields.Nested(data, many=many)
        if response_map:
            return schema_map
        return Schema.from_dict(schema_map)

    @staticmethod
    def mweb_api_paginate_response_schema(data):
        schema_map = MWebSwaggerSchema.mweb_api_response_data_schema(data, many=True, response_map=True)
        pagination_schema = Schema.from_dict({
            "page": fields.Integer(),
            "itemPerPage": fields.Integer(),
            "total": fields.Integer(),
            "totalPage": fields.Integer(),
        })
        schema_map["pagination"] = fields.Nested(pagination_schema)
        return Schema.from_dict(schema_map)

    @staticmethod
    def mweb_api_message_response_schema():
        schema_map = MWebSwaggerSchema.mweb_api_response_base_schema_map()
        schema_map["message"] = fields.String()
        return Schema.from_dict(schema_map)

    @staticmethod
    def mweb_api_error_response_schema():
        schema_map = MWebSwaggerSchema.mweb_api_response_base_schema_map()
        schema_map["message"] = fields.String()
        schema_map["error"] = fields.Dict(keys=fields.String(), values=fields.String())
        return Schema.from_dict(schema_map)
