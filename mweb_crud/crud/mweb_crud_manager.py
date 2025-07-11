from mweb_crud.common import MWebCRUDException
from mweb_crud.common.mweb_cb_helper import MWebCBHelper
from mweb_crud.common.mweb_crud_base import MWebCRUDBase
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.crud import RequestContext, ResponseMaker
from mweb_crud.data_transfer import MWebBaseDTO, MWebIDDTO, MWebDatedDTO, MWebDTO
from mweb_crud.helper import BeforeAfterSaveCallable
from mweb_orm import MWebBaseModel
from typing import Optional, Callable
from mweb_orm.query import MWebQueryProcessor


class CRUDManager(MWebCRUDBase):

    def __init__(self, model: type[MWebBaseModel]):
        self._request_context = RequestContext()
        self._response_maker = ResponseMaker()
        self._model = model
        self._cb_helper = MWebCBHelper()

    @property
    def request(self) -> RequestContext:
        return self._request_context

    @property
    def response(self) -> ResponseMaker:
        return self._response_maker

    @property
    def model(self) -> type[MWebBaseModel]:
        return self._model

    def raise_error(self, message: str, details: dict = None, error_code: int = None, http_code: int = None):
        raise MWebCRUDException(message=message, details=details, error_code=error_code, http_code=http_code)

    async def create(
            self,
            request: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO,
            response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO | None = None,
            response_message: str = None,
            data: dict = None,
            before_save: Optional[BeforeAfterSaveCallable] = None,
            after_save: Optional[BeforeAfterSaveCallable] = None,
            as_model: bool = False, allow_files: bool = False,
            before_validate: Optional[Callable[[dict], None]] = None,
            after_validate: Optional[Callable[[dict], None]] = None):

        if not data:
            data = await self._request_context.get_data(validator=request, before_validate=before_validate, after_validate=after_validate)

        saved_model = await self.save(data=data, request=request, before_save=before_save, after_save=after_save)
        if as_model:
            return saved_model

        if not saved_model.is_saved():
            return self._response_maker.error(message=MWebCRUDConfig.FAILED_TO_SAVE_DATA_MSG)

        if not response_message:
            response_message = MWebCRUDConfig.CREATE_SUCCESS_MSG
        return await self.make_success_response(model=saved_model, response_message=response_message, response=response)


    async def update(
            self,
            request: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO,
            response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO | None = None,
            response_message: str = None,
            data: dict = None,
            before_save: Optional[BeforeAfterSaveCallable] = None,
            after_save: Optional[BeforeAfterSaveCallable] = None,
            as_model: bool = False, allow_files: bool = False,
            before_validate: Optional[Callable[[dict], None]] = None,
            after_validate: Optional[Callable[[dict], None]] = None):
        pass

    async def details(self, model_id: int, response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, query: MWebQueryProcessor | None = None, as_model: bool = False):
        details = await self.get_by_id(model_id=model_id, query=query, raise_error=True)
        if as_model:
            return details
        return await self._response_maker.success_from_model(model=details, transformer=response)

    async def delete(self, model_id: int, response_message: str = None, query: MWebQueryProcessor | None = None, before_delete: Optional[Callable[[int, MWebBaseModel], None]] = None, after_delete: Optional[Callable[[int, MWebBaseModel], None]] = None):
        pass

    async def hard_delete(self, model_id: int, query: MWebQueryProcessor | None = None):
        pass

    async def read_all(self, response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, search_fields: list = None, sort_field: str | None = None, sort_order: str | None = None, sort: bool = True, query: MWebQueryProcessor | None = None, as_list: bool = False):
        result = await self.read_from_model(
            search_fields=search_fields,
            sort_field=sort_field,
            sort_order=sort_order,
            query=query,
            paginate=False,
            sort=sort,
        )

        if as_list:
            return result

        return await self._response_maker.success_from_model(model=result, transformer=response)

    async def paginated_read_all(self, response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, search_fields: list = None, sort_field: str | None = None, sort_order: str | None = None, sort: bool = True, item_per_page: int | None = None, query: MWebQueryProcessor | None = None, as_list: bool = False):
        result = await self.read_from_model(
            search_fields=search_fields,
            sort_field=sort_field,
            sort_order=sort_order,
            query=query,
            item_per_page=item_per_page,
            paginate=True,
            sort=sort,
        )

        if as_list:
            return result

        return await self._response_maker.success_from_model(model=result, transformer=response)
