# ═══════════════════════════════════════════════════════════════════════════════
# Tests for SG_Send__Browser__Test_Harness
# ═══════════════════════════════════════════════════════════════════════════════

import requests
from unittest                                                                   import TestCase
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                          import SG_Send__Browser__Test_Harness
from sg_send_qa.browser.Schema__Browser_Test_Config                             import Schema__Browser_Test_Config
from sg_send_qa.browser.SG_Send__Browser__Pages                                 import SG_Send__Browser__Pages


# ═══════════════════════════════════════════════════════════════════════════════
# Unit tests — no servers, no browser
# ═══════════════════════════════════════════════════════════════════════════════

class test_SG_Send__Browser__Test_Harness__port_reuse(TestCase):              # port-reuse logic (no browser)

    def test__load_saved_state__returns_none_in_headless_mode(self):           # CI isolation — headless=True always returns None
        harness = SG_Send__Browser__Test_Harness()
        assert harness.config.headless is True                                 # default is CI mode
        result = harness._load_saved_state()
        assert result is None                                                  # no disk read in CI mode

    def test__api_server_port_open__closed_port_returns_false(self):          # port not in use → False
        harness = SG_Send__Browser__Test_Harness()
        assert harness.api_server_port_open(0)     is False                   # port 0 is never open
        assert harness.api_server_port_open(19999) is False                   # unpopulated port

    def test__start_api_server__twice__no_port_conflict(self):                # two sequential start/stop cycles — no leftover port
        harness = SG_Send__Browser__Test_Harness()
        harness.headless(True)

        harness._start_api_server()                                           # first start
        assert harness.api_server is not None
        assert harness.api_server.is_port_open()                              # port is open after start
        port_first = harness.api_server.port
        harness.api_server.stop()                                             # clean up first

        harness._start_api_server()                                           # second start — fresh (headless=True, no saved port)
        assert harness.api_server is not None
        assert harness.api_server.is_port_open()                              # port is open after second start
        port_second = harness.api_server.port
        harness.api_server.stop()                                             # clean up second

        assert port_first  != 0                                               # both ports were real
        assert port_second != 0


class test_SG_Send__Browser__Test_Harness__hash_cache(TestCase):           # content-hash UI build cache (no browser)

    def test__ui_content_hash__returns_string(self):                        # _ui_content_hash() returns a non-empty string
        harness = SG_Send__Browser__Test_Harness()
        result  = harness._ui_content_hash()
        assert isinstance(result, str)
        assert len(result) > 0

    def test__stable_build_folder__returns_local_server(self):              # _stable_build_folder() ends in .local-server
        harness = SG_Send__Browser__Test_Harness()
        folder  = harness._stable_build_folder()
        assert isinstance(folder, str)
        assert folder.endswith('.local-server')

    def test__ui_content_hash__is_stable(self):                             # calling twice returns same value
        harness = SG_Send__Browser__Test_Harness()
        first   = harness._ui_content_hash()
        second  = harness._ui_content_hash()
        assert first == second


class test_SG_Send__Browser__Test_Harness(TestCase):

    def test__init__(self):                                                     # verify defaults before setup
        with SG_Send__Browser__Test_Harness() as _:
            assert type(_.config)  is Schema__Browser_Test_Config
            assert _.api_server   is None
            assert _.ui_folder    is None
            assert _.ui_server    is None
            assert _.sg_send      is None
            assert _.test_objs    is None

    def test__init____with_config(self):                                        # verify config passthrough
        config = Schema__Browser_Test_Config(headless=False)
        with SG_Send__Browser__Test_Harness(config=config) as _:
            assert _.config.headless is False

    def test__headless__fluent(self):                                           # headless() returns self for chaining
        harness = SG_Send__Browser__Test_Harness()
        result  = harness.headless(True)
        assert result is harness
        assert harness.config.headless is True

    def test__headless__default_is_true(self):                                  # .headless() with no arg defaults to True
        harness = SG_Send__Browser__Test_Harness()
        harness.headless()
        assert harness.config.headless is True

    def test__headless__false(self):                                            # .headless(False) sets debug mode
        harness = SG_Send__Browser__Test_Harness()
        harness.headless(False)
        assert harness.config.headless is False


# ═══════════════════════════════════════════════════════════════════════════════
# Integration tests — full stack (one harness shared across all tests)
# ═══════════════════════════════════════════════════════════════════════════════

class test_SG_Send__Browser__Test_Harness__lifecycle(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().headless(True).setup()

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    # ── Accessors ────────────────────────────────────────────────────────────

    def test_sg_send__type(self):
        assert type(self.harness.sg_send) is SG_Send__Browser__Pages

    def test_access_token__is_guid(self):
        token = self.harness.access_token()
        assert type(token) is str
        assert len(token)  > 0

    def test_api_url__format(self):
        assert 'http://localhost:' in self.harness.api_url()
        assert self.harness.api_url().endswith('/')

    def test_ui_url__format(self):
        assert 'http://localhost:' in self.harness.ui_url()
        assert self.harness.ui_url().endswith('/')

    # ── API server ───────────────────────────────────────────────────────────

    def test_api_server__docs(self):
        response = requests.get(self.harness.api_url() + 'api/docs')
        assert response.status_code == 200

    def test_api_server__openapi(self):
        response = requests.get(self.harness.api_url() + 'api/openapi.json')
        assert response.status_code == 200
        assert '/api/transfers/create' in response.json().get('paths', {})

    def test_access_token__works_against_api(self):                             # token from harness is accepted by the API
        token    = self.harness.access_token()
        response = requests.post(self.harness.api_url() + 'api/transfers/create'    ,
                                 json    = {"file_size_bytes": 100}                  ,
                                 headers = {"x-sgraph-access-token": token}          )
        assert response.status_code == 200
        assert 'transfer_id' in response.json()

    # ── UI server ────────────────────────────────────────────────────────────

    def test_ui_server__root(self):
        response = requests.get(self.harness.ui_url())
        assert response.status_code == 200

    def test_ui_server__en_gb(self):
        response = requests.get(self.harness.ui_url() + 'en-gb')
        assert response.status_code == 200

    def test_ui_server__qa_setup(self):
        response = requests.get(self.harness.ui_url() + '_common/qa-setup.html')
        assert response.status_code == 200

    # ── Browser ──────────────────────────────────────────────────────────────

    def test_browser__qa_setup_page(self):
        with self.harness.sg_send as _:
            _.page__qa_setup()
            assert _.title() == 'QA Setup'

    def test_browser__set_token_bypasses_gate(self):                            # token injection → gate bypassed → upload zone visible
        with self.harness.sg_send as _:
            _.storage__set_token(self.harness.access_token())
            _.page__root()
            assert _.is_access_gate_visible() is False
            assert _.upload_state()           == 'idle'