# todo I place this in this tests/qa/apis_for_sites folder because
#     - this needs a live website (first locally, but we should also support the multiple live sites)
#     - so it is not an unit test,
#     - could be an integration test
#     - but since we are going to also be adding a lot more sites here, and this is one of the set of tests that
#       the qa team will be executing in order to make the decision to go live or not with a nre release
#       this 'qa' folder felt right
#     - the idea is then to use these classes inside the v030 folder which should simplify that code quite a bit
#     - we might actually move these also to an v030 folder (or v03x or v04x) , since some of these tests will be version specific
#       which will be very relevant when we start to have test suites that need to run again multiple IFD versions
#
#
# todo first refactor that I'm going to do is the code in def _upload_with_simple_token(self, shots, filename="token-test.txt"):
#      from the tests/qa/v030/p0__friendly_token/test__friendly_token.py (see notes on that file, here is just the code)
#
#
#     def _upload_with_simple_token(self, shots, filename="token-test.txt"):
#         """Upload a file with Simple Token mode and return the friendly token string."""
#         self.sg_send.page__root()
#         self.sg_send.upload__set_file(filename, SAMPLE_CONTENT.encode())

#         shots.capture(self.sg_send.raw_page(), "01_file_selected", "File selected (delivery step active)")
#
#         self.sg_send.upload__click_next()
#         self.sg_send.upload__select_share_mode("token")
#         shots.capture(self.sg_send.raw_page(), "02_simple_token_selected", "Simple Token selected")
#         self.sg_send.upload__click_next()
#         self.sg_send.upload__wait_for_complete()
#         shots.capture(self.sg_send.raw_page(), "03_upload_complete", "Upload complete")
#
#         return self.sg_send.upload__get_friendly_token()

# @dev see how these imports are all aligned
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
    #     cls.upload_page.harness.teardown()          # todo: ok so this is why we where getting those errors

    def test_current_logic(self):
        with self.upload_page as _:
            _.current_logic()

    def test_debug_setup_chrome(self):
        with self.upload_page as _:
            _.debug_setup_chrome()

    @pytest.mark.skip("doesn't work when running with all tests") # todo: see below for the Async error
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
            # todo: we really need to figure out why this is happening, since this is the core reason we need to stop chrome between multiple class executions,
            #       and there are tons of cases where it would be a lot of efficient to keep the browser open
            #       for example in cases where we only want to setup once the access token

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
            # @dev @architect capture this pattern of using the OSbot_Utils __() and obj() and Type_Safe().obj() technique to write powerful assertions like the one below
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
                                                      stdout=__SKIP__,      # todo: see why we can't the capture stderr here
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
            #pprint(result.fast_api_process.stdout.read())      # @dev: question how do we read this?

            assert requests.get(result.url__server__info).status_code == 200    # confirm server is still up
            assert is_port_open('localhost', port)                    is True   # confirm port is open
            assert kill_process(pid)                                  is None   # @dev add note to OSBot-Utils that we shoud have an option to return true if the process existed and was stopped ok (maybe with an option for 'wait for close')
            assert wait_for_port_closed('localhost', port)            is True   # wait until port is closed
            assert is_port_open('localhost', port) is False           is False  # confirm port is closed

            try:
                requests.get(result.url__server__info)                          #   try to make a request (which will fail with the exception below)
            except Exception as error:
                assert str(error.args[0].reason) == (f"HTTPConnection(host='localhost', port={port}): "
                                                     f"Failed to establish a new connection: [Errno 61] Connection refused")
        # @qa , ok, so we now have the pattern we need
        #       - add the option to start the process
        #       - then store the pid
        #       - on next run: check if the pid is still there,
        #                      and if it is, check if port is open
        #                      and if it is, use it
        #                      if not, clean the entry in the file
        #       - when wanting to stop the server
        #                - kill the process
        #                - update the file


        # this is a note for the @librarian: can you take a look at the commit branch origin/claude/create-qa-explorer-team-Tg5A6
        #                                    and the diff between this version and what we currently have  in dev
        #                                    and see if we need to import any of that
        #                                    once we have that review done and extracted what we need, we can delete that branch


        # for @qa: can you take a look at the origin/claude/qa-site-v030-integration-Tg5A6 branch, since I also thin we can delete it