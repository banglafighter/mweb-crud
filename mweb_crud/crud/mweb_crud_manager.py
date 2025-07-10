from mweb_crud.common.mweb_crud_base import MWebCRUDBase
from mweb_crud.crud import RequestContext, ResponseMaker
from mweb_orm import MWebBaseModel


class CRUDManager(MWebCRUDBase):
    _request_context: RequestContext = None
    _response_maker: ResponseMaker = None
    _model: type[MWebBaseModel] = None

    def __init__(self, model: type[MWebBaseModel]):
        self._request_context = RequestContext()
        self._response_maker = ResponseMaker()
        self._model = model

    def request(self) -> RequestContext:
        return self._request_context

    def response(self) -> ResponseMaker:
        return self._response_maker

    def model(self) -> type[MWebBaseModel]:
        return self._model

    async def create(self, as_model: bool = False):
        pass

    async def details(self, as_model: bool = False):
        pass

    async def update(self, as_model: bool = False):
        pass

    async def delete(self):
        pass

    async def hard_delete(self):
        pass

    async def read_all(self, as_list: bool = False):
        pass

    async def paginated_read_all(self, as_object: bool = False):
        pass
