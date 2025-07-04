from quart import request
from mweb import MWebBase, SSRController, template
from mweb_crud.common.mweb_crud_config import MWebCRUDConfig
from mweb_crud.swagger.mweb_sd_processor import MWebSDProcessor
from mweb_crud.swagger.mweb_swagger_generator import MWebSwaggerGenerator


class MWebSwaggerUI:
    _mweb_app: MWebBase = None

    def register(self, mweb_app):
        self._mweb_app = mweb_app
        self.init_swagger_ssr_controller()

    def init_swagger_ssr_controller(self):
        if MWebCRUDConfig.ENABLE_SWAGGER_UI and self._mweb_app:
            controller = SSRController(
                name="MWebSwaggerSystem",
                package_name=__name__,
                template_dir="template-assets/templates",
                assets_dir="template-assets/assets",
                assets_url=MWebCRUDConfig.SWAGGER_UI_ASSETS_URL
            )
            controller.add_url_rule(MWebCRUDConfig.SWAGGER_JSON_URL, "swagger-json", self.swagger_json)
            controller.add_url_rule(MWebCRUDConfig.SWAGGER_UI_URL, "swagger-ui", self.swagger_ui)
            self._mweb_app.add_controller(controller)

    def swagger_ui(self):
        auth = self.check_auth()
        if auth:
            return auth
        return template.sync_render('swagger-ui.html', config=MWebCRUDConfig)

    def swagger_json(self):
        auth = self.check_auth()
        if auth:
            return auth
        decorator_processor = MWebSDProcessor(self._mweb_app)
        action_definitions = decorator_processor.get_action_definitions()
        mweb_swagger_generator = MWebSwaggerGenerator()
        mweb_swagger_generator.process_action_definitions(action_definitions)
        return mweb_swagger_generator.get_swagger_spec()

    def check_auth(self):
        if MWebCRUDConfig.ENABLE_SWAGGER_AUTH:
            auth = request.authorization
            username = MWebCRUDConfig.SWAGGER_AUTH_USERNAME
            password = MWebCRUDConfig.SWAGGER_AUTH_PASSWORD
            if not (auth and auth.username == username and auth.password == password):
                return ('You are not authorize to access the URL.', 401, {
                    'WWW-Authenticate': 'Basic realm="Login Required"'
                })
        return None
