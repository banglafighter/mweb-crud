from typing import Optional
from mweb_crud.common import MWebCRUDException
from mweb_crud.common.mweb_cb_helper import MWebCBHelper
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.crud import RequestContext, ResponseMaker
from mweb_crud.data_transfer import MWebDTO, MWebBaseDTO, MWebIDDTO, MWebDatedDTO
from mweb_crud.helper import BeforeAfterSaveCallable
from mweb_orm import MWebBaseModel, and_, MWebIDModel
from mweb_orm.query import MWebQueryProcessor


class MWebCRUDBase:
    _model: type[MWebBaseModel | MWebIDModel] = None
    _request_context: RequestContext = None
    _cb_helper: MWebCBHelper = None
    _response_maker: ResponseMaker = None

    async def make_success_response(self, model: MWebBaseModel, response_message: str = None, response: MWebBaseDTO = None):
        if response:
            return await self._response_maker.success_from_model(model=model, transformer=response, message=response_message)
        return await self._response_maker.success(content=response_message)

    async def check_unique(self):
        pass

    def _add_delete_filter(self, query: MWebQueryProcessor, only: bool = False):
        return self._cb_helper.filter_deleted(model=self._model, query=query, only=only)

    async def get_by_id(self, model_id: int, query: MWebQueryProcessor | None = None, raise_error: bool = True, message: str | None = None):
        if not query:
            query = self._model.query
        query = query.where(and_(self._model.id == model_id))
        return await self.get_first(query=query, message=message, raise_error=raise_error)

    async def get_first(self, query: MWebQueryProcessor, raise_error: bool = True, message: str | None = None):
        query = self._add_delete_filter(query=query)
        result = await query.first()
        if result:
            return result
        elif raise_error:
            if not message:
                message = MWebCRUDConfig.RECORD_NOT_FOUND_MSG
            raise MWebCRUDException(message=message)
        return None

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
            query: MWebQueryProcessor | None = None,
            search_fields: list | None = None,
            paginate: bool = True,
            is_deleted: bool = False,
            sort: bool = True,
            sort_field: str | None = None,
            sort_order: str | None = None,
            item_per_page: int | None = None,
            search_text: str | None = None):

        if not query:
            query = self._model.query

        query = self._add_delete_filter(query=query, only=is_deleted)

        if not item_per_page:
            item_per_page = MWebCRUDConfig.TOTAL_ITEM_PER_PAGE

        if not sort_field:
            sort_field = MWebCRUDConfig.SORT_DEFAULT_FIELD_NAME

        if not sort_order:
            sort_order = MWebCRUDConfig.SORT_DEFAULT_ORDER_NAME

        if sort:
            query = self._cb_helper.set_sorting(
                query=query,
                sort_field=sort_field,
                sort_order=sort_order,
                request_context=self._request_context,
                model=self._model,
            )

        query = self._cb_helper.set_search(
            model=self._model,
            request_context=self._request_context,
            query=query,
            search_fields=search_fields,
            search_text=search_text
        )

        if paginate:
            page: int = self._request_context.get_query_param(key=MWebCRUDConfig.PAGE_PARAM_NAME, default=1, type=int)
            item_per_page: int = self._request_context.get_query_param(key=MWebCRUDConfig.ITEM_PER_PAGE_PARAM_NAME, default=item_per_page, type=int)
            return await query.paginate(item_per_page=item_per_page, page=page)

        return await query.read_all()
