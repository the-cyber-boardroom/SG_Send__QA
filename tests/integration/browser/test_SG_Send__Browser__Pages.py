# ═══════════════════════════════════════════════════════════════════════════════
# Tests for SG_Send__Browser__Pages — Browser page primitives and workflows
# Requires: local QA stack running on localhost:10062
# ═══════════════════════════════════════════════════════════════════════════════
from pathlib                                                            import Path
from unittest                                                           import TestCase
from osbot_fast_api.utils.Fast_API_Server                               import Fast_API_Server
from osbot_utils.helpers.duration.decorators.print_duration             import print_duration
from osbot_utils.testing.Stderr                                         import Stderr
from osbot_utils.testing.Temp_Folder                                    import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                                import Temp_Web_Server
from sg_send_qa.browser.SG_Send__Browser__Pages                         import SG_Send__Browser__Pages
from sg_send_qa.utils.QA_UI_Server                                      import build_ui_serve_dir
from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import setup__send_user_lambda__test_client


class test_SG_Send__Browser__Pages(TestCase):                                   # Navigation — pages load with correct titles
    @classmethod
    def setUpClass(cls):
        cls.headless = True
        cls.stderr   = Stderr()                                                 # capture the message from chrome process and temp webserver (so that they don't pollute the console out)

        with print_duration(action_name='start api server'):
            cls.send_user_lambda__test_objs = setup__send_user_lambda__test_client()
            cls.api_server                  = Fast_API_Server(app=cls.send_user_lambda__test_objs.fast_api__app)
            cls.api_server.start()
            cls.api_url                     = f"http://localhost:{cls.api_server.port}/"

        with print_duration(action_name='build static server'):
            # UI server — build static files, serve them
            cls.ui_folder = Temp_Folder()
            cls.ui_folder.__enter__()
            build_ui_serve_dir(api_url   = cls.api_url             ,
                               serve_dir = Path(cls.ui_folder.path()))

        with print_duration(action_name='start static server'):
            cls.ui_server = Temp_Web_Server(root_folder = cls.ui_folder.path(),
                                            host        = 'localhost'          )   # localhost for Web Crypto secure context
            cls.ui_server.__enter__()

        with print_duration(action_name='start chrome'):
            cls.sg_send = SG_Send__Browser__Pages(headless    = cls.headless       ,
                                                  target_port = cls.ui_server.port )
            cls.chrome  = cls.sg_send.chrome()
            cls.ui_url  = f'http://localhost:{cls.ui_server.port}/'


        cls.stderr.start()                                                          # start capturing the console.err

    @classmethod
    def tearDownClass(cls):
        cls.stderr.stop()                                                           # stop capturing the console.err
        with print_duration(action_name='stop static server'):
            cls.ui_server.__exit__(None, None, None)                                # stops server, releases port
            cls.ui_folder.__exit__(None, None, None)                                # deletes temp folder
        with print_duration(action_name='stop api server'):
            cls.api_server.stop()

        if cls.headless:                                                            # if we are headless
            cls.sg_send.qa_browser().stop()
    # ── Page navigation ──────────────────────────────────────────────────────

    def test_page__root(self):                                                  # upload page loads
        self.sg_send.page__root()
        assert self.sg_send.title() == 'SG/Send — Zero-knowledge encrypted file sharing'

    def test_page__browse(self):                                                # browse page loads
        self.sg_send.page__browse()
        assert self.sg_send.title() == 'SG/Send — Browse Files'

    def test_page__download(self):                                              # download page loads
        self.sg_send.page__download()
        assert self.sg_send.title() == 'SG/Send — Download & Decrypt'

    def test_page__gallery(self):                                               # gallery page loads
        self.sg_send.page__gallery()
        assert self.sg_send.title() == 'SG/Send — Gallery'

    def test_page__view(self):                                                  # view page loads
        self.sg_send.page__view()
        assert self.sg_send.title() == 'SG/Send — View File'

    def test_page__welcome(self):                                               # welcome page loads
        self.sg_send.page__welcome()
        assert self.sg_send.title() == 'SG/Send — Welcome'


