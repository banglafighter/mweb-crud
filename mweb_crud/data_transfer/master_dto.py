from marshmallow import EXCLUDE, Schema
from sqlalchemy import inspect
from mweb_orm import MWebBaseModel


class MWebMasterDTO(Schema):
    model_class: type[MWebBaseModel] = None

    def _get_required_fields(self, model):
        mapper = inspect(model)
        required_fields = []
        for column in mapper.columns:
            if not column.nullable and not column.primary_key and column.default is None and column.server_default is None:
                required_fields.append(column.key)
        return required_fields

    def _get_model(self):
        if self.model_class and issubclass(self.model_class, MWebBaseModel):
            return self.model_class
        return None

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
            raise Exception(exception_messages)
        return name_value_pairs

    def _get_model_instance(self, data: dict):
        model = self._get_model()
        name_value_pairs = self._get_required_field_values(model, data, raise_exception=True)
        if model:
            return model(**name_value_pairs)
        return None

    def to_model(self, data: dict, model_instance: MWebBaseModel = None) -> MWebBaseModel | None:
        validated_dict = self.load(data=data, unknown=EXCLUDE)
        if not validated_dict or not isinstance(validated_dict, dict):
            return None

        if not model_instance:
            model_instance = self._get_model_instance(data)

        if model_instance:
            for key, value in data.items():
                if hasattr(model_instance, key) and key != "model_class":
                    setattr(model_instance, key, value)

        return model_instance

    def validate(self, data: dict | list, many: bool = False, partial: bool = False) -> dict:
        return super().validate(data, many=many, partial=partial)

    def to_dict(self, model: MWebBaseModel | list[MWebBaseModel], many: bool = False) -> dict:
        return self.dump(model, many=many)

    def clean_dict(self, data: dict) -> dict:
        return self.load(data=data, unknown=EXCLUDE)
