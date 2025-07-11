from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.crud import RequestContext
from mweb_orm.query import MWebQueryProcessor


# MWeb CRUD Base Helper
class MWebCBHelper:

    @classmethod
    def set_pagination(cls, query: MWebQueryProcessor, request_context: RequestContext, item_per_page: int | None = None):
        if item_per_page is None:
            item_per_page = MWebCRUDConfig.TOTAL_ITEM_PER_PAGE

    @classmethod
    def set_search(cls, request_context: RequestContext):
        pass

    @classmethod
    def filter_deleted(cls, only: bool = False):
        pass

    @classmethod
    def set_sorting(cls, request_context: RequestContext, sort_field: str | None = None, sort_order: str | None = None):
        pass
