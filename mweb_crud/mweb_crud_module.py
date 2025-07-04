from mweb import MWebBase, MWebConfig
from mweb.engine.mweb_util import MWebUtil
import mweb_crud.common.mweb_crud_config
from mweb_crud.swagger.mweb_swagger_ui import MWebSwaggerUI


class MWebCRUDModule:

    def register(self, mweb_app: MWebBase, config: MWebConfig):
        MWebUtil.copy_config_property(source=config, destination=mweb_crud.common.mweb_crud_config.MWebCRUDConfig)

        self.register_swagger(mweb_app=mweb_app)

    def register_swagger(self, mweb_app: MWebBase):
        mweb_swagger_ui = MWebSwaggerUI()
        mweb_swagger_ui.register(mweb_app)
