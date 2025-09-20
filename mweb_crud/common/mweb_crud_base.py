from typing import Optional
from mweb_crud.common import MWebCRUDException
from mweb_crud.common.mweb_cb_helper import MWebCBHelper
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.crud import RequestContext, ResponseMaker
from mweb_crud.data_transfer import MWebDTO, MWebBaseDTO, MWebIDDTO, MWebDatedDTO
from mweb_crud.helper import BeforeAfterSaveCallable, BeforeAfterDeleteCallable
from mweb_orm import MWebBaseModel, and_, MWebIDModel, MWebModel, make_transient
from mweb_orm.orm import mweb_orm
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

    def _add_delete_filter(self, query: MWebQueryProcessor, only: bool = False):
        return self._cb_helper.filter_deleted(model=self._model, query=query, only=only)

    async def get_by_id(self, record_id: int, query: MWebQueryProcessor | None = None, raise_error: bool = True, message: str | None = None) -> MWebBaseModel | MWebModel | None:
        if not query:
            query = self._model.query

        if isinstance(record_id, str):
            record_id = int(record_id)

        query = query.where(and_(self._model.id == record_id))
        return await self.get_first(query=query, message=message, raise_error=raise_error)

    async def get_by_ids(self, ids: list, query: MWebQueryProcessor | None = None, raise_error: bool = True, message: str | None = None) -> list[MWebBaseModel | MWebModel] | None:
        if not query:
            query = self._model.query
        query = self._add_delete_filter(query=query)
        result = await query.where(and_(self._model.id.in_(ids))).read_all()
        if result:
            return result
        elif raise_error:
            if not message:
                message = MWebCRUDConfig.RECORD_NOT_FOUND_MSG
            raise MWebCRUDException(message=message)
        return None

    async def hard_delete_by_ids(self, ids: list, query: MWebQueryProcessor | None = None):
        if not query:
            query = self._model.query
        await query.where(and_(self._model.id.in_(ids))).delete()

    async def get_first(self, query: MWebQueryProcessor, raise_error: bool = True, message: str | None = None) -> MWebBaseModel | None:
        query = self._add_delete_filter(query=query)
        result = await query.first()
        if result:
            return result
        elif raise_error:
            if not message:
                message = MWebCRUDConfig.RECORD_NOT_FOUND_MSG
            raise MWebCRUDException(message=message)
        return None

    async def save(self, data: dict, request: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, before_save: Optional[BeforeAfterSaveCallable] = None, after_save: Optional[BeforeAfterSaveCallable] = None, model_instance: MWebBaseModel | None = None, uuid: str | None = None, ignore_keys: list[str] | None = None) -> MWebBaseModel | None:
        model = request.to_model(data=data, model_instance=model_instance, ignore_keys=ignore_keys)
        if uuid:
            model.uuid = uuid

        if before_save and callable(before_save):
            await before_save(data=data, model=model)
        await model.save()

        if after_save and callable(after_save):
            await after_save(data=data, model=model)

        return model

    async def save_existing(self, record_id: int, data: dict, request: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, before_save: Optional[BeforeAfterSaveCallable] = None, after_save: Optional[BeforeAfterSaveCallable] = None, model_instance: MWebBaseModel | None = None, ignore_keys: list[str] | None = None, query: MWebQueryProcessor | None = None):
        if not model_instance:
            model_instance = await self.get_by_id(record_id=record_id, raise_error=True, query=query)
        return await self.save(data=data, request=request, before_save=before_save, after_save=after_save, model_instance=model_instance, ignore_keys=ignore_keys)

    async def soft_remove_by_model(self, delete_model, record_id: int = None, before_delete: Optional[BeforeAfterDeleteCallable] = None, after_delete: Optional[BeforeAfterDeleteCallable] = None):
        if not record_id and delete_model:
            record_id = delete_model.id

        if before_delete and callable(before_delete):
            await before_delete(record_id=record_id, existing_model=delete_model)

        if delete_model and hasattr(delete_model, "isDeleted"):
            delete_model.isDeleted = True
            await delete_model.save()

            if after_delete and callable(after_delete):
                await after_delete(record_id=record_id, existing_model=delete_model)

            return True
        return False

    async def soft_remove(self, record_id: int, query: MWebQueryProcessor | None = None, before_delete: Optional[BeforeAfterDeleteCallable] = None, after_delete: Optional[BeforeAfterDeleteCallable] = None):
        existing_model = await self.get_by_id(record_id=record_id, query=query, raise_error=True)
        return await self.soft_remove_by_model(delete_model=existing_model, record_id=record_id, before_delete=before_delete, after_delete=after_delete)

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

    async def check_unique(self, field_name: str, value, query: MWebQueryProcessor | None = None, not_record_id: int = None, raise_error: bool = True, message: str | None = None):
        if not query:
            query = self._model.query
        query = query.where(and_(getattr(self._model, field_name) == value))

        if not not_record_id:
            query =  query.where(and_(self._model.id != not_record_id))

        result = await query.first()

        if message is None:
            message = MWebCRUDConfig.VALUE_ALREADY_EXISTS_MSG

        if result and raise_error:
            raise MWebCRUDException(message=MWebCRUDConfig.DUPLICATE_ENTRY_ERROR_MSG, details={field_name: message})

    def clone(self, model, none_props: list = None):
        if model in mweb_orm.session:
            mweb_orm.session.expunge(model)
        make_transient(model)

        if not none_props:
            none_props = []

        reset_props = ["id", "uuid", "created", "updated"] + none_props
        for prop in reset_props:
            if hasattr(model, prop):
                setattr(model, prop, None)

        return model
