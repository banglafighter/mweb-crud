from dataclasses import dataclass
from mw_common import SDLize, DataUtil
from .base_dto import MWebBaseDTO, MWebDTO, MWebDatedDTO, MWebIDDTO


@dataclass(kw_only=True)
class MWebDtoData(SDLize):
    name: str
    isRequired: bool = False
    xlImport: bool = False
    xlExport: bool = False


class MWebCrudDtoUtil:

    @classmethod
    def get_dto_data(cls, dto: MWebBaseDTO | MWebDTO | MWebDatedDTO | MWebIDDTO) -> dict[str, MWebDtoData]:
        response: dict = {}
        for field in dto.declared_fields:
            field_data = DataUtil.dict_value(data=dto.declared_fields, key=field)
            if not field_data:
                continue
            dto_data = MWebDtoData(name=field)
            dto_data.isRequired = field_data.required

            if hasattr(field_data, "xlExport"):
                dto_data.xlExport = field_data.xlExport

            if hasattr(field_data, "xlImport"):
                dto_data.xlImport = field_data.xlImport

            response[field] = dto_data
        return response
