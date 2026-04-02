# [LIB-2026-04-01-042] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
import pytest
import requests
from unittest                                                                    import TestCase
from osbot_utils.testing.__                                                      import __, __SKIP__
from osbot_utils.utils.Http                                                      import is_port_open, wait_for_port_closed
from osbot_utils.utils.Process                                                   import kill_process
from sg_send_qa.apis_for_sites.send_sgraph_ai.pages.Page__Send_SGraph_Ai__Upload import Page__Send_SGraph_Ai__Upload


class test_Page__Send_SGraph_Ai__Upload(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upload_page = Page__Send_SGraph_Ai__Upload()

    # @classmethod
    # def tearDownClass(cls):
    #     cls.upload_page.harness.teardown()

    def test_current_logic(self):
        with self.upload_page as _:
            _.current_logic()

    def test_debug_setup_chrome(self):
        with self.upload_page as _:
            _.debug_setup_chrome()

    @pytest.mark.skip("doesn't work when running with all tests")
    def test_debug_inner_calls_of_setup(self):
        with self.upload_page as _:
            _.debug_inner_calls_of_setup()
            # >               raise Error(
            #                     """It looks like you are using Playwright Sync API inside the asyncio loop.
            #     Please use the Async API instead."""
            #                 )
            # E               playwright._impl._errors.Error: It looks like you are using Playwright Sync API inside the asyncio loop.
            # E               Please use the Async API instead.
            #
            # [LIB-2026-04-01-043] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

    def test_debug_start_api_server(self):
        with self.upload_page as _:
            _.debug_start_api_server()

    def test_debug_start_api_server__with_saved_state(self):
        with self.upload_page as _:
            _.debug_start_api_server__with_saved_state()

    def test_debug_inner_methods_of__start_api_server(self):
        with self.upload_page as _:
            _.debug_inner_methods_of__start_api_server()

    def test_debug__start_and_stop_server_using_port(self):
        with self.upload_page as _:
            result = _.debug__start_and_stop_server_using_port()
            pid    = result.pid
            port   = result.port
            stderr = result.stderr
            stdout = result.stdout
            # [LIB-2026-04-01-044] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
            assert result == __(fast_api_process = __(_waitpid_lock=__SKIP__,
                                                      _input=None,
                                                      _communication_started=False,
                                                      args=[ 'poetry',
                                                             'run',
                                                             'uvicorn',
                                                             'sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user:app',
                                                             '--port',
                                                             str(port),
                                                             '--log-level',
                                                             'info',
                                                             '--timeout-graceful-shutdown',
                                                             '0'],
                                                      stdin=None,
                                                      stdout=__SKIP__,
                                                      stderr=__SKIP__,
                                                      pid=pid,
                                                      returncode=None,
                                                      encoding=None,
                                                      errors=None,
                                                      pipesize=-1,
                                                      text_mode=None,
                                                      _sigint_wait_secs=0.25,
                                                      _closed_child_pipe_fds=True,
                                                      _child_created=True),
                                stderr      = stderr ,
                                stdout      = stdout ,
                                pid         = pid    ,
                                port        = port   ,
                                url__server       = f'http://localhost:{port}',
                                url__server__info = f'http://localhost:{port}/info/status' )

            #pprint(result.fast_api_process.stdout.flush())
            #pprint(result.fast_api_process.stdout.read())

            assert requests.get(result.url__server__info).status_code == 200    # confirm server is still up
            assert is_port_open('localhost', port)                    is True   # confirm port is open
            assert kill_process(pid)                                  is None   # [LIB-2026-04-01-045] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
            assert wait_for_port_closed('localhost', port)            is True   # wait until port is closed
            assert is_port_open('localhost', port) is False           is False  # confirm port is closed

            try:
                requests.get(result.url__server__info)                          #   try to make a request (which will fail with the exception below)
            except Exception as error:
                assert str(error.args[0].reason) == (f"HTTPConnection(host='localhost', port={port}): "
                                                     f"Failed to establish a new connection: [Errno 61] Connection refused")
        # [LIB-2026-04-01-046] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md