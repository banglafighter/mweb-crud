from . import dto
from .master_dto import MWebMasterDTO


class MWebBaseDTO(MWebMasterDTO):
    pass


class MWebIDDTO(MWebMasterDTO):
    id = dto.Integer(dump_only=True)


class MWebDatedDTO(MWebIDDTO):
    created = dto.DateTime(dump_only=True, format="%d %b %Y %I:%M:%S %p")
    updated = dto.DateTime(dump_only=True, format="%d %b %Y %I:%M:%S %p")


class MWebDTO(MWebDatedDTO):
    uuid = dto.String(dump_only=True)
