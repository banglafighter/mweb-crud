from uuid import UUID
from mw_common import DataUtil, MwUtil
from ..common import MWebCRUDException
from ..common.mweb_cb_helper import MWebCBHelper
from ..common.mweb_crud_base import MWebCRUDBase
from ..common.mweb_crud_config import MWebCRUDConfig
from ..crud import RequestContext, ResponseMaker
from ..data_transfer import MWebBaseDTO, MWebIDDTO, MWebDatedDTO, MWebDTO
from ..file_upload import MWebCRUDFile, UploadCustomizer
from ..helper import BeforeAfterSaveCallable, BeforeAfterDeleteCallable
from mweb_orm import MWebBaseModel, MWebQueryProcessor
from typing import Optional, Callable


class CRUDManager(MWebCRUDBase):
    _mweb_crud_file: MWebCRUDFile = None

    def __init__(self, model: type[MWebBaseModel]):
        self._request_context = RequestContext()
        self._response_maker = ResponseMaker()
        self._model = model
        self._cb_helper = MWebCBHelper()
        self._mweb_crud_file = MWebCRUDFile()

    @property
    def request(self) -> RequestContext:
        return self._request_context

    @property
    def response(self) -> ResponseMaker:
        return self._response_maker

    @property
    def model(self) -> type[MWebBaseModel]:
        return self._model

    def raise_error(self, message: str, details: dict | None = None, error_code: int | None = None, http_code: int | None = None):
        raise MWebCRUDException(message=message, details=details, error_code=error_code, http_code=http_code)

    async def create(
            self,
            request: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO,
            response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO | None = None,
            response_message: str = None,
            data: dict = None,
            before_save: Optional[BeforeAfterSaveCallable] = None,
            after_save: Optional[BeforeAfterSaveCallable] = None,
            as_model: bool = False,
            allow_files: bool = False,
            upload_customizer: UploadCustomizer | None = None,
            upload_path: str | None = None,
            ignore_keys: list[str] | None = None,
            before_validate: Optional[Callable[[dict], None]] = None,
            after_validate: Optional[Callable[[dict], None]] = None,
            allow_fsp: bool = False):

        if data is None:
            clean = False
            read_from = "json"
            if allow_files:
                read_from = "form"
                clean = True
            data = await self._request_context.get_data(validator=request, before_validate=before_validate, after_validate=after_validate, read_from=read_from, clean=clean)

        fsp: str | None = None
        if allow_fsp:
            fsp = MwUtil.fsp()

        uuid: UUID | None = None
        if allow_files:
            uuid = MwUtil.uuid7()
            data = await self._mweb_crud_file.process_and_upload_files(request=request, upload_path=upload_path, upload_customizer=upload_customizer, data=data, uuid=str(uuid), fsp=fsp)

        saved_model = await self.save(data=data, request=request, before_save=before_save, after_save=after_save, uuid=uuid, ignore_keys=ignore_keys, fsp=fsp)
        if as_model:
            return saved_model

        if not saved_model.is_saved():
            return await self._response_maker.error(message=MWebCRUDConfig.FAILED_TO_SAVE_DATA_MSG)

        if not response_message:
            response_message = MWebCRUDConfig.CREATE_SUCCESS_MSG
        return await self.make_success_response(model=saved_model, response_message=response_message, response=response)

    async def update(
            self,
            request: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO,
            response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO | None = None,
            response_message: str | None = None,
            data: dict | None = None,
            before_save: Optional[BeforeAfterSaveCallable] = None,
            after_save: Optional[BeforeAfterSaveCallable] = None,
            as_model: bool = False,
            allow_files: bool = False,
            upload_customizer: UploadCustomizer | None = None,
            upload_path: str | None = None,
            model_instance: MWebBaseModel | None = None,
            ignore_keys: list[str] | None = None,
            query: MWebQueryProcessor | None = None,
            before_validate: Optional[Callable[[dict], None]] = None,
            after_validate: Optional[Callable[[dict], None]] = None,
            allow_fsp: bool = False,
            pull_by: str = "id"):

        if data is None:
            clean = False
            read_from = "json"
            if allow_files:
                read_from = "form"
                clean = True
            data = await self._request_context.get_data(validator=request, before_validate=before_validate, after_validate=after_validate, read_from=read_from, clean=clean)

        uuid: str | UUID | None = None
        record_id: int | None = None
        if pull_by == "uuid":
            uuid = DataUtil.dict_value(data=data, key="uuid")
            if not uuid and not model_instance:
                self.raise_error(message=MWebCRUDConfig.ID_REQUIRED_MSG)
            uuid = self.to_uuid(uuid=uuid)
        else:
            record_id = DataUtil.dict_value(data=data, key="id")
            if not record_id and not model_instance:
                self.raise_error(message=MWebCRUDConfig.ID_REQUIRED_MSG)

        fsp: str | None = None
        if allow_files:
            if not model_instance:
                if record_id:
                    model_instance = await self.get_by_id(record_id=record_id, raise_error=True, query=query)
                elif uuid:
                    model_instance = await self.get_by_uuid(uuid=uuid, raise_error=True, query=query)
            existing_uuid = model_instance.uuid

            if allow_fsp and hasattr(model_instance, "fsp"):
                fsp = getattr(model_instance, "fsp", None)
            if allow_fsp and not fsp:
                fsp = MwUtil.fsp()
            data = await self._mweb_crud_file.process_and_upload_files(request=request, upload_path=upload_path, upload_customizer=upload_customizer, data=data, uuid=existing_uuid, fsp=fsp)

        updated_model = await self.save_existing(record_id=record_id, uuid=uuid, data=data, request=request, before_save=before_save, after_save=after_save, model_instance=model_instance, ignore_keys=ignore_keys, query=query, fsp=fsp)
        if as_model:
            return updated_model

        if not updated_model.is_saved():
            return await self._response_maker.error(message=MWebCRUDConfig.FAILED_TO_UPDATE_DATA_MSG)

        if not response_message:
            response_message = MWebCRUDConfig.UPDATE_SUCCESS_MSG
        return await self.make_success_response(model=updated_model, response_message=response_message, response=response)

    async def details(self, record_id: int | None = None, response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO | None = None, uuid: str | None = None, query: MWebQueryProcessor | None = None, as_model: bool = False, as_transform: bool = False):
        if record_id:
            details = await self.get_by_id(record_id=record_id, query=query, raise_error=True)
        elif uuid:
            details = await self.get_by_uuid(uuid=uuid, query=query, raise_error=True)
        else:
            raise MWebCRUDException(message=MWebCRUDConfig.RECORD_ID_OR_UUID_REQUIRED_MSG)

        if as_model:
            return details
        elif not response:
            raise MWebCRUDException(message=MWebCRUDConfig.DTO_IS_REQUIRED_MSG)

        return await self._response_maker.success_from_model(model=details, transformer=response, as_transform=as_transform)

    async def delete(self, record_id: int | None = None, uuid: str | None = None, response_message: str | None = None, query: MWebQueryProcessor | None = None, before_delete: Optional[BeforeAfterDeleteCallable] = None, after_delete: Optional[BeforeAfterDeleteCallable] = None):
        if not response_message:
            response_message = MWebCRUDConfig.DELETE_SUCCESS_MSG
        if not record_id and not uuid:
            raise MWebCRUDException(message=MWebCRUDConfig.RECORD_ID_OR_UUID_REQUIRED_MSG)

        is_removed = await self.soft_remove(record_id=record_id, uuid=uuid, query=query, before_delete=before_delete, after_delete=after_delete)
        if is_removed:
            return await self._response_maker.success(content=response_message)
        return await self._response_maker.error(message=MWebCRUDConfig.FAILED_TO_DELETE_RECORD_MSG)

    async def read_all(self, response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, search_fields: list | dict | None = None, sort_field: str | None = None, sort_order: str | None = None, sort: bool = True, query: MWebQueryProcessor | None = None, as_list: bool = False, as_dict: bool = False, as_transform: bool = False):
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

        return await self._response_maker.success_from_model(model=result, transformer=response, as_dict=as_dict, as_transform=as_transform)

    async def paginated_read_all(self, response: MWebDTO | MWebBaseDTO | MWebIDDTO | MWebDatedDTO, search_fields: list | dict | None = None, sort_field: str | None = None, sort_order: str | None = None, sort: bool = True, item_per_page: int | None = None, query: MWebQueryProcessor | None = None, as_list: bool = False, as_dict: bool = False, as_transform: bool = False):
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

        return await self._response_maker.success_from_model(model=result, transformer=response, as_dict=as_dict, as_transform=as_transform)

    async def hard_delete(self, record_id: int, query: MWebQueryProcessor | None = None):
        existing_model = await self.get_by_id(record_id=record_id, query=query, raise_error=True)
        await existing_model.delete()
        return await self._response_maker.success(content=MWebCRUDConfig.DELETE_SUCCESS_MSG)
