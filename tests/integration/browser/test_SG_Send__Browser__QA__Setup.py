import requests
from pathlib                                                                import Path
from unittest                                                               import TestCase
from osbot_fast_api.utils.Fast_API_Server                                   import Fast_API_Server
from osbot_utils.helpers.duration.decorators.print_duration                 import print_duration
from osbot_utils.testing.Temp_Folder                                        import Temp_Folder
from osbot_utils.testing.Temp_Web_Server                                    import Temp_Web_Server
from osbot_utils.utils.Misc                                                 import list_set
from sg_send_qa.browser.SG_Send__Browser__Pages                             import SG_Send__Browser__Pages
from sg_send_qa.utils.QA_UI_Server                                          import build_ui_serve_dir
from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import setup__send_user_lambda__test_client


class test_SG_Send__Browser__setup(TestCase):                            # Page state queries
    sg_send : SG_Send__Browser__Pages

    @classmethod
    def setUpClass(cls):
        cls.headless    = True
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

        with print_duration(action_name='startic static server'):
            cls.ui_server = Temp_Web_Server(root_folder = cls.ui_folder.path(),
                                            host        = 'localhost'          )   # localhost for Web Crypto secure context
            cls.ui_server.__enter__()

            cls.sg_send = SG_Send__Browser__Pages(headless=cls.headless,
                                                  target_port = cls.ui_server.port)
            cls.ui_url  = f'http://localhost:{cls.ui_server.port}/'



    @classmethod
    def tearDownClass(cls):
        with print_duration(action_name='stop static server'):
            cls.ui_server.__exit__(None, None, None)                                # stops server, releases port
            cls.ui_folder.__exit__(None, None, None)                                # deletes temp folder
        with print_duration(action_name='stop api server'):
            cls.api_server.stop()

        if cls.headless:                                                            # if we are headless
            cls.sg_send.qa_browser().stop()


    # ── QA Setup ───────────────────────────────────────────────────────

    def test__page__qa_setup(self):
        with self.sg_send as _:
            assert _.page__qa_setup().url() == f'http://localhost:{self.ui_server.port}/_common/qa-setup.html'
            assert _.title()                == 'QA Setup'

    def test__storage__dump(self):
        with self.sg_send as _:
            qa_dump = _.storage__dump()
            assert qa_dump == {}

    def test__storage__set_token(self):
        token = 'an-token'
        with self.sg_send as _:
            qa_dump = _.storage__set_token(token).storage__dump()
            assert qa_dump == {'sgraph-send-token': token }
