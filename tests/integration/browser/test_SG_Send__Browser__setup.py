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
        cls.headless = True
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

            cls.sg_send = SG_Send__Browser__Pages(headless    = cls.headless      ,
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


    # ── check local servers ───────────────────────────────────────────────────────

    def test_check_test_server(self):
        assert self.api_url == f"http://localhost:{self.api_server.port}/"
        assert self.ui_url  == f"http://localhost:{self.ui_server.port}/"


        page__api__root     = requests.get(self.api_url, allow_redirects=False)
        path__api__docs     = requests.get(self.api_url + 'api/docs')
        path__api__open_api = requests.get(self.api_url + 'api/openapi.json')

        assert page__api__root    .status_code == 404
        assert path__api__docs    .status_code == 200
        assert path__api__open_api.status_code == 200

        assert list_set(path__api__open_api.json().get('paths')) == ['/api/early-access/signup', '/api/presigned/abort/{transfer_id}/{upload_id}', '/api/presigned/capabilities',
                                                                     '/api/presigned/complete', '/api/presigned/download-url/{transfer_id}', '/api/presigned/initiate',
                                                                     '/api/presigned/upload-url/{transfer_id}', '/api/transfers/check-token/{token_name}',
                                                                     '/api/transfers/complete/{transfer_id}', '/api/transfers/create', '/api/transfers/download-base64/{transfer_id}',
                                                                     '/api/transfers/download/{transfer_id}', '/api/transfers/info/{transfer_id}', '/api/transfers/upload/{transfer_id}',
                                                                     '/api/transfers/validate-token/{token_name}', '/api/vault/batch/{vault_id}', '/api/vault/delete/{vault_id}',
                                                                     '/api/vault/delete/{vault_id}/{file_id}', '/api/vault/health/{vault_id}', '/api/vault/list/{vault_id}',
                                                                     '/api/vault/read-base64/{vault_id}', '/api/vault/read-base64/{vault_id}/{file_id}',
                                                                     '/api/vault/read/{vault_id}', '/api/vault/read/{vault_id}/{file_id}',
                                                                     '/api/vault/write/{vault_id}', '/api/vault/write/{vault_id}/{file_id}', '/api/vault/zip/{vault_id}',
                                                                     '/info/health', '/info/server', '/info/status', '/info/version', '/info/versions']


        page__ui__root            = requests.get(self.ui_url, allow_redirects=False)
        path__ui__en_gb           = requests.get(self.ui_url + 'en-gb')
        path__ui__en_gb_browse    = requests.get(self.ui_url + 'en-gb/browse')
        path__ui__common_qa_setup = requests.get(self.ui_url + '_common/qa-setup.html')


        assert page__ui__root           .status_code == 200
        assert path__ui__en_gb          .status_code == 200
        assert path__ui__en_gb_browse   .status_code == 200
        assert path__ui__common_qa_setup.status_code == 200