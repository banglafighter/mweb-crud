from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.crud import RequestContext
from mweb_orm import MWebBaseModel, and_, MWebIDModel, or_
from mweb_orm.query import MWebQueryProcessor


# MWeb CRUD Base Helper
class MWebCBHelper:

    @classmethod
    def set_search(cls, model: type[MWebBaseModel | MWebIDModel], request_context: RequestContext, query: MWebQueryProcessor, search_fields: list | None = None, search_text: str = None):
        like = []

        if not search_fields or len(search_fields) == 0:
            return query

        search = search_text
        if not search:
            search = request_context.get_query_param(key=MWebCRUDConfig.SEARCH_FIELD_PARAM_NAME, default=None)

        if search:
            for field in search_fields:
                like.append(getattr(model, field).ilike("%{}%".format(search)))
            if like:
                return query.where(or_(*like))

        return query

    @classmethod
    def filter_deleted(cls, model: type[MWebBaseModel | MWebIDModel], query: MWebQueryProcessor, only: bool = False):
        if hasattr(model, "isDeleted"):
            query = query.where(and_(getattr(model, "isDeleted") == only))
        return query

    @classmethod
    def set_sorting(cls, request_context: RequestContext, model: type[MWebBaseModel | MWebIDModel], query: MWebQueryProcessor, sort_field: str | None = None, sort_order: str | None = None):
        sort_field = request_context.get_query_param(key=MWebCRUDConfig.SORT_FIELD_PARAM_NAME, default=sort_field)
        sort_order = request_context.get_query_param(key=MWebCRUDConfig.SORT_ORDER_PARAM_NAME, default=sort_order)

        default_order = MWebCRUDConfig.SORT_DEFAULT_ORDER_NAME
        if sort_order and (sort_order != "asc" and sort_order != "desc"):
            sort_order = default_order

        if not sort_order or not sort_field:
            return query

        if sort_order == "asc":
            return query.order_by(getattr(model, sort_field).asc())

        return query.order_by(getattr(model, sort_field).desc())
