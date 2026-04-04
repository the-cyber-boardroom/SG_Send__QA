# [LIB-2026-04-01-042] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
import pytest
import requests
from unittest                                                                    import TestCase
from osbot_utils.testing.__                                                      import __, __SKIP__
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.utils.Http                                                      import is_port_open, wait_for_port_closed
from osbot_utils.utils.Process                                                   import kill_process
from sg_send_qa.apis_for_sites.send_sgraph_ai.pages.Page__Send_SGraph_Ai__Upload import Page__Send_SGraph_Ai__Upload
from sg_send_qa.browser.Schema__Browser_Test_Config                              import Schema__Browser_Test_Config


# ═══════════════════════════════════════════════════════════════════════════════
# Non-browser unit tests — run in CI without Chromium
# ═══════════════════════════════════════════════════════════════════════════════

class test_Page__Send_SGraph_Ai__Upload__Unit(TestCase):
    """Unit tests for Page__Send_SGraph_Ai__Upload — no browser required."""

    def test_instantiation(self):                                             # class can be constructed with no arguments
        page = Page__Send_SGraph_Ai__Upload()
        assert page is not None

    def test_is_type_safe_subclass(self):                                     # must be a Type_Safe subclass (project convention)
        page = Page__Send_SGraph_Ai__Upload()
        assert isinstance(page, Type_Safe)

    def test_config_defaults_to_headless_true(self):                         # CI safety: headless must default to True
        page = Page__Send_SGraph_Ai__Upload()
        assert isinstance(page.config, Schema__Browser_Test_Config)
        assert page.config.headless is True

    def test_config_can_be_overridden_to_headless_false(self):               # debug path: caller can force visible browser
        config = Schema__Browser_Test_Config(headless=False)
        page   = Page__Send_SGraph_Ai__Upload(config=config)
        assert page.config.headless is False

    def test_harness_is_none_before_setup(self):                             # harness must not be started until setup() is called
        page = Page__Send_SGraph_Ai__Upload()
        assert page.harness is None

    def test_sg_send_is_none_before_setup(self):                             # sg_send (browser pages) must not exist until setup()
        page = Page__Send_SGraph_Ai__Upload()
        assert page.sg_send is None

    def test_has_setup_method(self):                                         # setup() must be present and callable
        page = Page__Send_SGraph_Ai__Upload()
        assert callable(getattr(page, 'setup', None))

    def test_has_upload_file_method(self):                                   # upload_file() must be present and callable
        page = Page__Send_SGraph_Ai__Upload()
        assert callable(getattr(page, 'upload_file', None))

    def test_has_get_friendly_token_method(self):                            # get_friendly_token() must be present and callable
        page = Page__Send_SGraph_Ai__Upload()
        assert callable(getattr(page, 'get_friendly_token', None))

    def test_has_teardown_method(self):                                      # teardown() must be present and callable
        page = Page__Send_SGraph_Ai__Upload()
        assert callable(getattr(page, 'teardown', None))

    def test_teardown_is_safe_when_harness_is_none(self):                    # teardown() must not raise if setup() was never called
        page = Page__Send_SGraph_Ai__Upload()
        page.teardown()                                                       # should complete without error


# ═══════════════════════════════════════════════════════════════════════════════
# Browser tests — require Chromium; skip in headless CI
# ═══════════════════════════════════════════════════════════════════════════════

class test_Page__Send_SGraph_Ai__Upload(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upload_page = Page__Send_SGraph_Ai__Upload()

    # @classmethod
    # def tearDownClass(cls):
    #     cls.upload_page.harness.teardown()

    @pytest.mark.skip("requires browser — run manually")
    def test_setup_and_teardown_headless(self):                              # verify headless setup/teardown lifecycle
        page = Page__Send_SGraph_Ai__Upload()
        page.setup()
        assert page.harness   is not None
        assert page.sg_send   is not None
        assert page.config.headless is True
        page.teardown()

    @pytest.mark.skip("requires browser — run manually")
    def test_upload_file_returns_friendly_token(self, tmp_path):             # upload a temp file and get back a word-word-NNNN token
        import re
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("headless upload test content")
            tmp_file = f.name
        try:
            page = Page__Send_SGraph_Ai__Upload()
            page.setup()
            token = page.upload_file(tmp_file)
            page.teardown()
            assert token, "upload_file() returned empty token"
            assert re.match(r"\b[a-z]+-[a-z]+-\d{4}\b", token), \
                f"Token does not match word-word-NNNN: {token!r}"
        finally:
            os.unlink(tmp_file)

    @pytest.mark.skip("requires browser — run manually")
    def test_current_logic(self):
        with self.upload_page as _:
            _.current_logic()

    @pytest.mark.skip("requires browser — run manually")
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

    @pytest.mark.skip("requires browser — run manually")
    def test_debug_start_api_server(self):
        with self.upload_page as _:
            _.debug_start_api_server()

    @pytest.mark.skip("requires browser — run manually")
    def test_debug_start_api_server__with_saved_state(self):
        with self.upload_page as _:
            _.debug_start_api_server__with_saved_state()

    @pytest.mark.skip("requires browser — run manually")
    def test_debug_inner_methods_of__start_api_server(self):
        with self.upload_page as _:
            _.debug_inner_methods_of__start_api_server()

    @pytest.mark.skip("requires browser — run manually")
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


# ═══════════════════════════════════════════════════════════════════════════════
# Integration tests — require Chromium and a running SG/Send instance; skip in CI
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.skip("requires browser — run manually")
class test_Page__Send_SGraph_Ai__Upload__Integration(TestCase):
    """Integration tests for Page__Send_SGraph_Ai__Upload — browser required.

    These tests exercise the full upload flow through a real headless Chromium
    browser against a running SG/Send instance.  They are skipped in CI because
    Chromium is not available in the sandbox; run them locally with:

        pytest tests/qa/apis_for_sites/send_sgraph_ai/pages/ -k Integration -s
    """

    @classmethod
    def setUpClass(cls):
        import os, re, tempfile
        cls._os             = os
        cls._re             = re
        cls._token_pattern  = re.compile(r"\b[a-z]+-[a-z]+-\d{4}\b")
        cls.page            = Page__Send_SGraph_Ai__Upload()
        cls.page.setup()

        # Create a small temp file once — reused across tests in this class
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("SG/Send QA integration test — upload via Page__Send_SGraph_Ai__Upload.")
            cls._tmp_file = f.name

        # Perform the upload once; store the token for all assertions
        cls._token = cls.page.upload_file(cls._tmp_file)

    @classmethod
    def tearDownClass(cls):
        cls.page.teardown()
        if hasattr(cls, '_tmp_file') and cls._os.path.exists(cls._tmp_file):
            cls._os.unlink(cls._tmp_file)

    def test_upload_file__returns_friendly_token(self):                          # upload_file() must return a non-empty friendly token
        assert self._token, "upload_file() returned an empty string — expected a friendly token"
        assert isinstance(self._token, str), f"upload_file() must return str, got {type(self._token)}"
        assert self._token_pattern.search(self._token), (
            f"Token does not match word-word-NNNN pattern: {self._token!r}"
        )

    def test_get_friendly_token__after_upload(self):                             # get_friendly_token() must return the same token as upload_file()
        page_token = self.page.get_friendly_token()
        assert page_token, "get_friendly_token() returned an empty string after upload"
        assert self._token_pattern.search(page_token), (
            f"get_friendly_token() result does not match word-word-NNNN pattern: {page_token!r}"
        )
        assert page_token == self._token, (
            f"get_friendly_token() returned {page_token!r} but upload_file() returned {self._token!r} — they must match"
        )

    def test_upload_page__is_accessible(self):                                   # root page loaded successfully — basic smoke check
        assert self.page.harness         is not None, "harness must be set after setup()"
        assert self.page.sg_send         is not None, "sg_send must be set after setup()"
        assert self.page.config.headless is True,     "headless must default to True (CI safety)"