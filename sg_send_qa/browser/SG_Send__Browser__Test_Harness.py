# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — Browser Test Harness
# Manages the full local stack lifecycle (API server + UI server + browser)
# for integration tests. Extracts the common setUpClass/tearDownClass pattern.
#
# Debug mode (headless=False):
#   - Ports are persisted to disk → same port across runs → localStorage survives
#   - UI build is cached by version → skip rebuild if unchanged
#   - set_access_token() checks before acting → usually a no-op
#
# CI mode (headless=True):
#   - Fresh random ports every run → full isolation
#   - No persistence → clean state guaranteed
# ═══════════════════════════════════════════════════════════════════════════════

from pathlib                                                                import Path
from osbot_fast_api.utils.Fast_API_Server                                   import Fast_API_Server
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.testing.Stderr                                             import Stderr
from osbot_utils.testing.Temp_Folder                                        import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                                    import Temp_Web_Server
from osbot_utils.utils.Files                                                import path_combine, temp_folder_current, folder_create, folder_exists
from sg_send_qa.browser.SG_Send__Browser__Pages                             import SG_Send__Browser__Pages
from sg_send_qa.browser.Schema__Browser_Test_Config                         import Schema__Browser_Test_Config
from sg_send_qa.browser.Harness_State__Persistence                          import Harness_State__Persistence, Schema__Harness_State
from sg_send_qa.utils.QA_UI_Server                                          import build_ui_serve_dir
from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import setup__send_user_lambda__test_client, Send__User_Lambda__Test_Objs


UI_BUILD_FOLDER_FORMAT = 'sg_send_qa_ui_build_{version}'


class SG_Send__Browser__Test_Harness(Type_Safe):                                # manages API server + UI server + browser lifecycle
    config          : Schema__Browser_Test_Config                               # session configuration
    persistence     : Harness_State__Persistence                                # load/save state across runs

    api_server      : Fast_API_Server               = None                      # FastAPI on stable port (in-memory backend)
    ui_folder       : Temp_Folder                   = None                      # temp dir with built static files (or cached)
    ui_server       : Temp_Web_Server               = None                      # static file server on stable port
    stderr          : Stderr                        = None                      # stderr capture (Chrome + server logs)
    sg_send         : SG_Send__Browser__Pages       = None                      # browser page primitives
    test_objs       : Send__User_Lambda__Test_Objs  = None                      # Send__User_Lambda__Test_Objs
    ui_serve_dir    : str                           = ''                        # resolved path to UI files (always full path)

    # ═══════════════════════════════════════════════════════════════════════════
    # Lifecycle
    # ═══════════════════════════════════════════════════════════════════════════

    def setup(self):                                                            # start everything — call from setUpClass
        saved_state = self._load_saved_state()
        self._start_api_server(saved_state)
        self._build_ui(saved_state)
        self._start_ui_server(saved_state)
        self._create_browser()
        self._save_state()
        if self.config.capture_stderr:
            self.stderr = Stderr()
            self.stderr.start()
        return self

    def teardown(self):                                                         # stop everything — call from tearDownClass
        if self.stderr:
            self.stderr.stop()
        if self.ui_server:
            self.ui_server.__exit__(None, None, None)
        if self.ui_folder and self.config.headless:                             # only delete build folder in CI mode
            self.ui_folder.__exit__(None, None, None)                           # debug mode keeps the cached build
        if self.api_server:
            self.api_server.stop()
        if self.config.headless and self.sg_send:
            self.sg_send.qa_browser().stop()
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Accessors
    # ═══════════════════════════════════════════════════════════════════════════

    def access_token(self) -> str:                                              # the auto-generated access token
        return self.test_objs.access_token

    def headless(self, value=True):                                             # note: call before .setup()
        self.config.headless = value
        return self

    def api_url(self) -> str:                                                   # e.g. http://localhost:54321/
        return f"http://{self.config.host}:{self.api_server.port}/"

    def ui_url(self) -> str:                                                    # e.g. http://localhost:63960/
        return f"http://{self.config.host}:{self.ui_server.port}/"

    # ═══════════════════════════════════════════════════════════════════════════
    # Util methods
    # ═══════════════════════════════════════════════════════════════════════════

    def set_access_token(self):                                                 # inject token, skip if already set
        token = self.access_token()
        with self.sg_send as _:
            current_token = None
            current_url   = _.url()

            if str(self.ui_server.port) in current_url:                         # already on the right origin
                try:
                    current_token = _.invoke__javascript(                        # check localStorage directly
                        "localStorage.getItem('sgraph-send-token');")
                except Exception:
                    pass

                if current_token == token:                                          # token already set — no-op
                    return current_token
                else:
                    _.storage__set_token(token=token)                                   # inject token
                    return token
            else:
                _.page__qa_setup()                                                  # navigate to lightweight page
                _.storage__set_token(token=token)                                   # inject token
                return token

    # ═══════════════════════════════════════════════════════════════════════════
    # Internal setup steps
    # ═══════════════════════════════════════════════════════════════════════════

    def _load_saved_state(self):                                                # load previous state (debug mode only)
        if self.config.headless:
            return None                                                         # CI mode — always fresh
        state = self.persistence.load()
        if state and self.persistence.ports_in_use(state):                      # stale servers from crashed test
            print(f"[harness] WARNING: ports {state.api_port}/{state.ui_port} still in use from previous run")
        return state

    def _start_api_server(self, saved_state=None):
        self.test_objs  = setup__send_user_lambda__test_client()
        api_port        = saved_state.api_port if saved_state else 0            # 0 = let Fast_API_Server pick random
        self.api_server = Fast_API_Server(app  = self.test_objs.fast_api__app ,
                                          port = api_port                      )
        self.api_server.start()



    def _build_ui(self, saved_state=None):
        ui_version = self._current_ui_version()

        if not self.config.headless and saved_state:
            cached_folder = saved_state.ui_build_folder
            if (saved_state.ui_version == ui_version
                    and cached_folder
                    and folder_exists(cached_folder)
                    and saved_state.api_port == self.api_server.port):
                self.ui_serve_dir = cached_folder               # reuse cached — skip rebuild
                return

        if self.config.headless:
            self.ui_folder = Temp_Folder()
            self.ui_folder.__enter__()
            self.ui_serve_dir = self.ui_folder.path()           # Temp_Folder manages lifecycle
        else:
            self.ui_serve_dir = self._stable_build_folder(ui_version)
            folder_create(self.ui_serve_dir)

        build_ui_serve_dir(api_url   = self.api_url()              ,
                           serve_dir = Path(self.ui_serve_dir)     )

    def _start_ui_server(self, saved_state=None):
        ui_port = saved_state.ui_port if saved_state and not self.config.headless else 0
        self.ui_server = Temp_Web_Server(root_folder = self.ui_serve_dir   ,
                                         host        = self.config.host    ,
                                         port        = ui_port             )
        self.ui_server.__enter__()

    # def _start_ui_server(self, saved_state=None):
    #     ui_port   = saved_state.ui_port if saved_state and not self.config.headless else 0
    #     serve_dir = self.ui_folder.folder_name if self.ui_folder.folder_name else self.ui_folder.path()
    #     self.ui_server = Temp_Web_Server(root_folder = serve_dir           ,
    #                                      host        = self.config.host    ,
    #                                      port        = ui_port             )
    #     self.ui_server.__enter__()

    def _create_browser(self):
        self.sg_send = SG_Send__Browser__Pages(headless    = self.config.headless  ,
                                               target_port = self.ui_server.port   )

    def _save_state(self):
        if self.config.headless:
            return
        state = Schema__Harness_State(
            api_port        = self.api_server.port                             ,
            ui_port         = self.ui_server.port                              ,
            ui_build_folder = self.ui_serve_dir                                ,   # ← was self.ui_folder.folder_name
            ui_version      = self._current_ui_version()                       ,
            access_token    = self.access_token()                              ,
            chrome_port     = 10070                                            )
        self.persistence.save(state)

    def _current_ui_version(self):                                              # read from the QA project version
        try:
            version_file = Path(__file__).parent.parent / 'version'
            return version_file.read_text().strip()
        except Exception:
            return 'unknown'

    def transfer_helper(self):                                                  # create transfers via API (no browser needed)
        from sg_send_qa.utils.QA_Transfer_Helper import QA_Transfer_Helper
        return QA_Transfer_Helper(api_url      = self.api_url().rstrip("/"),  # strip trailing slash — helper adds its own
                                  access_token = self.access_token()      )

    def _stable_build_folder(self, version):                                    # debug mode: stable path in temp
        folder_name = UI_BUILD_FOLDER_FORMAT.format(version=version)
        return path_combine(temp_folder_current(), folder_name)