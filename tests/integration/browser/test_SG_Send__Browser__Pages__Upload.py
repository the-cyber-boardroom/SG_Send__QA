from pathlib import Path
from unittest                                                               import TestCase
from osbot_fast_api.utils.Fast_API_Server                                   import Fast_API_Server
from osbot_utils.helpers.duration.decorators.print_duration                 import print_duration
from osbot_utils.testing.Stderr                                             import Stderr
from osbot_utils.testing.Temp_Folder                                        import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                                    import Temp_Web_Server
from sg_send_qa.browser.SG_Send__Browser__Pages                             import SG_Send__Browser__Pages
from sg_send_qa.utils.QA_UI_Server                                          import build_ui_serve_dir
from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import setup__send_user_lambda__test_client


class test_SG_Send__Browser__Pages__Upload(TestCase):                           # Upload wizard — needs full local stack with valid token
    sg_send      : SG_Send__Browser__Pages
    access_token : str

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
        cls.page_setup()                                                            # setup this test-suite environment

    @classmethod
    def tearDownClass(cls):
        cls.stderr.stop()                                                           # stop capturing the console.err
        with print_duration(action_name='stop static server'):
            cls.ui_server.__exit__(None, None, None)                                # stops server, releases port
            cls.ui_folder.__exit__(None, None, None)                                # deletes temp folder
        with print_duration(action_name='stop api server'):
            cls.api_server.stop()

        if cls.headless:                                                            # if we are headless
            cls.sg_send.qa_browser().stop()                                         # close the browser



    @classmethod
    def page_setup(cls):
        cls.access_token = cls.send_user_lambda__test_objs.access_token
        with cls.sg_send as _:
            _.page__qa_setup()
            _.storage__set_token(token=cls.access_token)        # make sure access token is set
            _.page__root()

    # ── Upload step-by-step ──────────────────────────────────────────────────

    def test_upload__set_file(self):                                            # file input works through shadow DOM
        print('here')
        return
        if self.sg_send.is_access_gate_visible() and self.access_token:
            self.sg_send.access_gate__enter_and_submit(self.access_token)
        self.sg_send.upload__set_file("test.txt", b"hello world")
        state = self.sg_send.upload_state()
        assert state in ('file-ready', 'choosing-delivery')                     # wizard advanced past idle

    def test_upload__click_next__to_share_step(self):                           # Next advances to share mode selection
        self.sg_send.page__root()
        self.sg_send.wait_for_page_ready()
        if self.sg_send.is_access_gate_visible() and self.access_token:
            self.sg_send.access_gate__enter_and_submit(self.access_token)
        self.sg_send.upload__set_file("test.txt", b"hello world")
        self.sg_send.upload__click_next()
        state = self.sg_send.upload_state()
        assert state == 'choosing-share'

    def test_upload__select_share_mode__combined(self):                          # selecting combined auto-advances to confirm
        self.sg_send.page__root()
        self.sg_send.wait_for_page_ready()
        if self.sg_send.is_access_gate_visible() and self.access_token:
            self.sg_send.access_gate__enter_and_submit(self.access_token)
        self.sg_send.upload__set_file("test.txt", b"hello world")
        self.sg_send.upload__click_next()
        self.sg_send.upload__select_share_mode("combined")
        state = self.sg_send.upload_state()
        assert state == 'confirming'