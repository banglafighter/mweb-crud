from marshmallow import EXCLUDE, Schema, RAISE
from sqlalchemy import inspect
from mweb_crud.common import MWebCRUDException
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_orm import MWebBaseModel, MWebModel, MWebDatedModel, MWebIDModel


class MWebMasterDTO(Schema):
    class Meta:
        model: type[MWebBaseModel] = None

    def _get_required_fields(self, model):
        required_fields = []
        if model:
            mapper = inspect(model)
            for column in mapper.columns:
                if not column.nullable and not column.primary_key and column.default is None and column.server_default is None:
                    required_fields.append(column.key)
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

    def to_model(self, data: dict, model_class: type[MWebBaseModel] = None, model_instance: MWebModel | MWebDatedModel | MWebIDModel | MWebBaseModel = None) -> MWebBaseModel | MWebModel | MWebDatedModel | MWebIDModel | None:
        self.validate(data=data, many=False, partial=False)
        validated_dict = self.load(data=data, unknown=EXCLUDE)
        if not validated_dict or not isinstance(validated_dict, dict):
            return None

        if not model_instance:
            model_instance = self._get_model_instance(validated_dict, model_class=model_class)

        if model_instance:
            for key, value in validated_dict.items():
                if hasattr(model_instance, key) and key != "model_class":
                    setattr(model_instance, key, value)

        return model_instance

    def validate(self, data: dict | list, many: bool = False, partial: bool = False) -> dict | list:
        setattr(self, "unknown", EXCLUDE)
        errors = super().validate(data, many=many, partial=partial)
        setattr(self, "unknown", RAISE)
        if errors and isinstance(errors, dict) and len(errors):
            raise MWebCRUDException(message=MWebCRUDConfig.DATA_VALIDATION_ERROR_MSG, details=errors)
        return data

    def to_dict(self, model: MWebBaseModel | list[MWebBaseModel], many: bool = False) -> dict | list:
        return self.dump(model, many=many)

    def clean_dict(self, data: dict | list, many: bool = False, partial: bool = False) -> dict | list:
        self.validate(data=data, many=many, partial=partial)
        return self.load(data=data, unknown=EXCLUDE)
