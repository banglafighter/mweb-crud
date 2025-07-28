from marshmallow import EXCLUDE, Schema, RAISE
from sqlalchemy import inspect
from mw_common import DataUtil
from mweb_crud.common import MWebCRUDException
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_orm import MWebBaseModel, MWebModel, MWebDatedModel, MWebIDModel
from dataclasses import fields


class MWebMasterDTO(Schema):
    class Meta:
        model: type[MWebBaseModel] = None

    def _get_snake_camel_name_map(self, model):
        mapping: dict = {}
        for field in fields(model):
            if hasattr(model, field.name):
                property_definition = getattr(model, field.name)
                if hasattr(property_definition, 'name') and hasattr(property_definition, "key"):
                    mapping[property_definition.name] = property_definition.key
        return mapping

    def _get_required_fields(self, model):
        required_fields = []
        if model:
            snake_camel_name_mapping: dict = self._get_snake_camel_name_map(model)
            mapper = inspect(model)
            for column in mapper.columns:
                if not column.nullable and not column.primary_key and column.default is None and column.server_default is None:
                    camel_case_name = DataUtil.dict_value(snake_camel_name_mapping, column.name)
                    if camel_case_name is not None:
                        required_fields.append(camel_case_name)
        return required_fields

    def _get_model(self, model_class: type[MWebBaseModel] = None):
        if not model_class:
            model_class = self.Meta.model
            if not issubclass(model_class, MWebBaseModel):
                raise MWebCRUDException(message=f"The specified model is invalid.")

        if model_class and issubclass(model_class, MWebBaseModel):
            return model_class
        else:
            raise MWebCRUDException(message=f"Please add model class inside a Meta class")

    def _get_required_field_values(self, model, data: dict, raise_exception=True):
        required_fields = self._get_required_fields(model)
        name_value_pairs: dict = {}
        exception_messages = {}
        for required_field in required_fields:
            if required_field not in data or data.get(required_field) is None:
                exception_messages[required_field] = "Required field '{}' is missing".format(required_field)
            else:
                name_value_pairs[required_field] = data.get(required_field)
        if exception_messages and len(exception_messages) and raise_exception:
            raise MWebCRUDException(message=MWebCRUDConfig.DATA_VALIDATION_ERROR_MSG, details=exception_messages)
        return name_value_pairs

    def _get_model_instance(self, data: dict, model_class: type[MWebBaseModel] = None):
        model = self._get_model(model_class=model_class)
        name_value_pairs = self._get_required_field_values(model, data, raise_exception=True)
        if model:
            return model(**name_value_pairs)
        return None

    def ignore_fields(self, data: dict, ignore_keys: list[str]) -> dict:
        if not ignore_keys or not data:
            return data
        return {key: value for key, value in data.items() if key not in ignore_keys}

    def to_model(self, data: dict, model_class: type[MWebBaseModel] = None, model_instance: MWebModel | MWebDatedModel | MWebIDModel | MWebBaseModel = None, ignore_keys: list[str] | None = None) -> MWebBaseModel | MWebModel | MWebDatedModel | MWebIDModel | None:
        self.validate(data=data, many=False, partial=False)
        validated_dict = self.load(data=data, unknown=EXCLUDE)
        if not validated_dict or not isinstance(validated_dict, dict):
            return None

        if ignore_keys:
            validated_dict = self.ignore_fields(data=validated_dict, ignore_keys=ignore_keys)

        if not model_instance:
            model_instance = self._get_model_instance(validated_dict, model_class=model_class)

        if model_instance:
            for key, value in validated_dict.items():
                if hasattr(model_instance, key) and key != "model_class":
                    setattr(model_instance, key, value)

        return model_instance

    def validate(self, data: dict | list, many: bool = False, partial: bool = False) -> dict | None:
        setattr(self, "unknown", EXCLUDE)
        errors = super().validate(data, many=many, partial=partial)
        setattr(self, "unknown", RAISE)
        if errors and isinstance(errors, dict) and len(errors):
            raise MWebCRUDException(message=MWebCRUDConfig.DATA_VALIDATION_ERROR_MSG, details=errors)
        return None

    def to_dict(self, model: MWebBaseModel | list[MWebBaseModel], many: bool = False) -> dict | list:
        return self.dump(model, many=many)

    def clean_dict(self, data: dict | list, many: bool = False, partial: bool = False) -> dict | list:
        return self.load(data=data, many=many, partial=partial, unknown="exclude")
