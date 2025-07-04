import types
from mweb import MWebBase
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.common.mweb_crud_const import SwaggerCommon
from mweb_crud.swagger.mweb_swagger_data import SwaggerData


class MWebSDProcessor:
    _mweb_app: MWebBase = None
    _ignore_verbs = {"HEAD", "OPTIONS"}
    _swagger_data_type_mapping = {
        "string": "string",
        "int": "integer",
        "float": "number",
        "path": "string",
        "any": "string",
        "uuid": "string"
    }

    def __init__(self, mweb_app: MWebBase):
        self._mweb_app = mweb_app

    def get_action_definitions(self):
        definitions = []
        for rule in self._mweb_app.url_map.iter_rules():
            endpoint = self._mweb_app.view_functions[rule.endpoint]
            if isinstance(endpoint, types.FunctionType):
                function_name = endpoint.__name__
                if function_name and self._is_it_swagger_definition(endpoint):
                    definition = endpoint(pass_definition=True)
                    definition = self._process_action_decorator(definition, rule)
                    if definition:
                        definitions.append(definition)
        return definitions

    def _is_it_swagger_definition(self, endpoint) -> bool:
        try:
            name = endpoint.__mweb_swagger__
            if name == SwaggerCommon.MWEB_SWAGGER:
                return True
        except:
            return False
        return False

    def _process_action_decorator(self, definition: SwaggerData, rule):
        definition = self._get_url_params(definition, rule)
        definition.methods = self._get_action_methods(rule, definition)
        definition = self._get_default_tag_name(definition, rule)
        return definition

    def _get_url_params(self, definition: SwaggerData, rule) -> SwaggerData:
        path = []
        url_and_data_type = self._extract_url_to_params(rule.rule)
        data_type = url_and_data_type['url_map']
        for param in rule.arguments:
            if param in data_type:
                path.append((param, data_type[param], True))
        definition.url = url_and_data_type['url']
        if definition.url_params and isinstance(definition.url_params, list):
            definition.url_params.extend(path)
        else:
            definition.url_params = path
        return definition

    def _extract_url_to_params(self, url):
        url_map = {}
        if url:
            fragments = url.split("/")
            for fragment in fragments:
                if fragment and fragment.startswith("<"):
                    actual_fragment = fragment
                    type_input = fragment.replace("<", "").replace(">", "").split(":")
                    if len(type_input) == 2 and (type_input[0] in self._swagger_data_type_mapping):
                        param_name = type_input[1]
                        url_map[param_name] = self._swagger_data_type_mapping[type_input[0]]
                    else:
                        url_map[type_input[0]] = "string"
                        param_name = type_input[0]
                    url = url.replace(actual_fragment, "{" + param_name + "}")
        return {"url": url, "url_map": url_map}

    def _get_action_methods(self, rule, definition: SwaggerData):
        methods = []
        if definition.method:
            methods.append(definition.method)
            return methods
        for method in rule.methods.difference(self._ignore_verbs):
            methods.append(method)
        return methods

    def _get_default_tag_name(self, definition: SwaggerData, rule):
        if definition.tag:
            definition.tags.append(definition.tag)
            return definition
        endpoint_name = rule.endpoint
        end = endpoint_name.find(".")
        total = len(endpoint_name)
        definition.tags = []
        if end != -1 and total > end:
            endpoint_name = endpoint_name[0:end]
            endpoint_name = endpoint_name.replace("_", " ")
            endpoint_name = endpoint_name.title()
            definition.tags.append(endpoint_name)
        else:
            definition.tags.append(MWebCRUDConfig.SWAGGER_DEFAULT_TAG_NAME)
        return definition
