from mweb_crud.data_transfer.master_dto import MWebMasterDTO


class MWebBaseDTO(MWebMasterDTO):
    pass


class MWebIDDTO(MWebMasterDTO):
    pass


class MWebDatedDTO(MWebIDDTO):
    pass


class MWebDTO(MWebDatedDTO):
    pass
