from typing import Optional
from mweb_crud.common.mweb_cb_helper import MWebCBHelper
from mweb_crud.crud import RequestContext, ResponseMaker
from mweb_crud.data_transfer import MWebDTO, MWebBaseDTO, MWebIDDTO, MWebDatedDTO
from mweb_crud.helper import BeforeAfterSaveCallable
from mweb_orm import MWebBaseModel
from mweb_orm.query import MWebQueryProcessor


class MWebCRUDBase:
    _model: type[MWebBaseModel] = None
    _request_context: RequestContext = None
    _cb_helper: MWebCBHelper = None
    _response_maker: ResponseMaker = None

    async def make_success_response(self, model: MWebBaseModel, response_message: str = None, response: MWebBaseDTO = None):
        if response:
            return await self._response_maker.success_from_model(model=model, transformer=response, message=response_message)
        return await self._response_maker.success(content=response_message)

    async def check_unique(self):
        pass

    async def get_by_id(self, model_id: int, query: MWebQueryProcessor | None = None, raise_error: bool = True, message: str | None = None):
        pass

    async def get_first(self, query: MWebQueryProcessor, raise_error: bool = True, message: str | None = None):
        pass

    async def save(self, data: dict, request: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, before_save: Optional[BeforeAfterSaveCallable] = None, after_save: Optional[BeforeAfterSaveCallable] = None, model_instance: MWebBaseModel | None = None):
        model = request.to_model(data=data, model_instance=model_instance)

        if before_save and callable(before_save):
            before_save(data=data, model=model)
        await model.save()

        if after_save and callable(after_save):
            after_save(data=data, model=model)

        return model

    async def save_existing(self):
        pass

    async def soft_remove(self):
        pass

    def clone(self):
        pass

    async def read_from_model(
            self,
            query: MWebQueryProcessor,
            search_fields: list | None = None,
            paginate: bool = True,
            is_deleted: bool = False,
            sort: bool = True,
            sort_field: str | None = None,
            sort_order: str | None = None,
            item_per_page: int | None = None,
            search_text: str | None = None):
        pass
