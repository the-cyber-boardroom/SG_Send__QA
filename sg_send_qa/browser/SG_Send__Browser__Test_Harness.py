# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — Browser Test Harness
# Manages the full local stack lifecycle (API server + UI server + browser)
# for integration tests. Extracts the common setUpClass/tearDownClass pattern.
# ═══════════════════════════════════════════════════════════════════════════════

from pathlib                                                                import Path
from osbot_fast_api.utils.Fast_API_Server                                   import Fast_API_Server
from osbot_utils.helpers.duration.decorators.capture_duration import capture_duration
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.testing.Stderr                                             import Stderr
from osbot_utils.testing.Temp_Folder                                        import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                                    import Temp_Web_Server
from sg_send_qa.browser.SG_Send__Browser__Pages                             import SG_Send__Browser__Pages
from sg_send_qa.browser.Schema__Browser_Test_Config                         import Schema__Browser_Test_Config
from sg_send_qa.utils.QA_UI_Server                                          import build_ui_serve_dir
from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import setup__send_user_lambda__test_client, Send__User_Lambda__Test_Objs

# todo: rename all variables and methods that start with _ to not use _  (i.e. these are not internal methods or variables)
#       add a class to capture all important durations that we have here (like we had in the previous mode)
            # with capture_duration as duration__action_abc:
            #     pass
            #
            # durations.action_abc = duration__action_abc.duration # this returns the duration value in seconds

class SG_Send__Browser__Test_Harness(Type_Safe):                                # manages API server + UI server + browser lifecycle
    config          : Schema__Browser_Test_Config                               # session configuration

    _api_server     : Fast_API_Server               = None                      # FastAPI on random port (in-memory backend)
    _ui_folder      : Temp_Folder                   = None                      # temp dir with built static files
    _ui_server      : Temp_Web_Server               = None                      # static file server on random port
    _stderr         : Stderr                        = None                      # stderr capture (Chrome + server logs)
    _sg_send        : SG_Send__Browser__Pages       = None                      # browser page primitives
    _test_objs      : Send__User_Lambda__Test_Objs  = None                      # Send__User_Lambda__Test_Objs

    # ═══════════════════════════════════════════════════════════════════════════
    # Lifecycle
    # ═══════════════════════════════════════════════════════════════════════════

    def setup(self):                                                            # start everything — call from setUpClass
        self._start_api_server()
        self._build_ui()
        self._start_ui_server()
        self._create_browser()
        if self.config.capture_stderr:
            self._stderr = Stderr()
            self._stderr.start()
        return self

    def teardown(self):                                                         # stop everything — call from tearDownClass
        if self._stderr:
            self._stderr.stop()
        if self._ui_server:
            self._ui_server.__exit__(None, None, None)
        if self._ui_folder:
            self._ui_folder.__exit__(None, None, None)
        if self._api_server:
            self._api_server.stop()
        if self.config.headless and self._sg_send:
            self._sg_send.qa_browser().stop()
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Accessors
    # ═══════════════════════════════════════════════════════════════════════════

    def sg_send(self) -> SG_Send__Browser__Pages:                               # the browser page API
        return self._sg_send

    def access_token(self) -> str:                                              # the auto-generated access token
        return self._test_objs.access_token

    def headless(self, value=True):                                                  # note: when setting this to False, this needs to be called before the .setup() method
        self.config.headless = value
        return self

    def api_url(self) -> str:                                                   # e.g. http://localhost:54321/
        return f"http://{self.config.host}:{self._api_server.port}/"

    def ui_url(self) -> str:                                                    # e.g. http://localhost:63960/
        return f"http://{self.config.host}:{self._ui_server.port}/"

    # ═══════════════════════════════════════════════════════════════════════════
    # Internal setup steps
    # ═══════════════════════════════════════════════════════════════════════════

    def _start_api_server(self):
        self._test_objs = setup__send_user_lambda__test_client()
        self._api_server = Fast_API_Server(app=self._test_objs.fast_api__app)
        self._api_server.start()

    def _build_ui(self):                                                    # todo: optimise this so that we don't need to build the static content all the time, in fact, use the current qa project version value to determine if we need to rebuild these files
        self._ui_folder = Temp_Folder()
        self._ui_folder.__enter__()
        build_ui_serve_dir(api_url   = self.api_url()                  ,
                           serve_dir = Path(self._ui_folder.path())    )

    def _start_ui_server(self):
        self._ui_server = Temp_Web_Server(root_folder = self._ui_folder.path() ,
                                          host        = self.config.host       )
        self._ui_server.__enter__()

    def _create_browser(self):
        self._sg_send = SG_Send__Browser__Pages(headless    = self.config.headless  ,
                                                target_port = self._ui_server.port  )


    # ═══════════════════════════════════════════════════════════════════════════
    # Util methods
    # ═══════════════════════════════════════════════════════════════════════════

    def set_access_token(self):                                 # todo: optimise this so that we detect if the current page has the token already (so that we don't need to open the QA page)
        with self._sg_send as _:
            try:
                current_token = _.invoke__javascript("localStorage.getItem('sgraph-send-token');")      # check if the token is already setup
            except:             # todo: add a better way to find this (for example we could check the URL)
                pass            #
            if current_token:                                                                       # if it is
                return current_token                                                                #   just return it and no need to open the QA page (which will flicker the screen
            else:
                valid_token= self.access_token()                                                    # if there is no token setup, get the one set on server setup
                _.page__qa_setup()                                                                  # go to the qa-setup page
                _.storage__set_token(token=valid_token)                                             # and set it there
                return valid_token                                                                  # and return the token set