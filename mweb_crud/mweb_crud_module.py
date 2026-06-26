from mweb import MWebBase, MWebConfig, MWebHook, MWebUtil
import mweb_crud.common.mweb_crud_config
from .common import MWebCRUDException
from .swagger.mweb_swagger_ui import MWebSwaggerUI


class MWebCRUDModule:

    def register(self, mweb_app: MWebBase, config: MWebConfig, hook: MWebHook):
        MWebUtil.copy_config_property(source=config, destination=mweb_crud.common.mweb_crud_config.MWebCRUDConfig)

        self.register_swagger(mweb_app=mweb_app)
        self.register_exception_handler(mweb_app=mweb_app)

    def register_swagger(self, mweb_app: MWebBase):
        mweb_swagger_ui = MWebSwaggerUI()
        mweb_swagger_ui.register(mweb_app)

    def register_exception_handler(self, mweb_app: MWebBase):
        mweb_app.register_exception_handler(exception_class=MWebCRUDException, handler=MWebCRUDException().handle_exception)
