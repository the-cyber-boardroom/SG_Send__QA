# ═══════════════════════════════════════════════════════════════════════════════
# Tests for SG_Send__Browser__Test_Harness
# ═══════════════════════════════════════════════════════════════════════════════
import pytest
import requests
from unittest                                                                   import TestCase
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                          import SG_Send__Browser__Test_Harness
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                          import Schema__Browser_Test_Config
from sg_send_qa.browser.SG_Send__Browser__Pages                                 import SG_Send__Browser__Pages


class test_SG_Send__Browser__Test_Harness(TestCase):                            # Unit tests — no servers needed

    def test__init__(self):                                                     # verify defaults before setup
        with SG_Send__Browser__Test_Harness() as _:
            assert type(_.config)  is Schema__Browser_Test_Config
            assert _._api_server   is None
            assert _._ui_folder    is None
            assert _._ui_server    is None
            assert _._sg_send      is None
            assert _._test_objs    is None

    def test__init____with_config(self):                                        # verify config passthrough
        config = Schema__Browser_Test_Config(headless=False)
        with SG_Send__Browser__Test_Harness(config=config) as _:
            assert _.config.headless is False


# class test_SG_Send__Browser__Test_Harness__lifecycle(TestCase):                 # Integration — starts/stops full stack

    def test_setup_and_teardown(self):                                          # full lifecycle: setup → verify → teardown
        harness = SG_Send__Browser__Test_Harness().setup()

        # verify accessors return sensible values
        assert type(harness.sg_send())      is SG_Send__Browser__Pages
        assert type(harness.access_token()) is str
        assert len(harness.access_token())  > 0                                 # random GUID, not empty
        assert 'http://localhost:'          in harness.api_url()
        assert 'http://localhost:'          in harness.ui_url()

        # verify API server is reachable
        api_response = requests.get(harness.api_url() + 'api/docs')
        assert api_response.status_code == 200

        # verify UI server is reachable
        ui_response = requests.get(harness.ui_url() + 'en-gb')
        assert ui_response.status_code == 200

        # verify qa-setup.html is served
        qa_response = requests.get(harness.ui_url() + '_common/qa-setup.html')
        assert qa_response.status_code == 200

        # verify browser can navigate
        with harness.sg_send() as _:
            _.page__qa_setup()
            assert _.title() == 'QA Setup'

        # teardown
        harness.teardown()

    def test__bug__teardown__idempotent(self):                                        # calling teardown twice currently raises error
        harness = SG_Send__Browser__Test_Harness().setup()
        harness.teardown()
        with pytest.raises(IndexError, match="pop from empty list"):
            harness.teardown()                                                      # second call is not safe

    def test_access_token__matches_api(self):                                   # token from harness works against the API
        harness = SG_Send__Browser__Test_Harness().setup()
        token   = harness.access_token()

        # create a transfer using the token — proves it's valid
        response = requests.post(harness.api_url() + 'api/transfers/create'    ,
                                 json    = {"file_size_bytes": 100}             ,
                                 headers = {"x-sgraph-access-token": token}    )
        assert response.status_code == 200
        assert 'transfer_id' in response.json()

        harness.teardown()

    def test_storage__set_token__bypasses_gate(self):                           # token injection via qa-setup.html works end-to-end
        harness = SG_Send__Browser__Test_Harness().setup()

        with harness.sg_send() as _:
            _.storage__set_token(harness.access_token())
            _.page__root()
            assert _.is_access_gate_visible() is False                          # gate bypassed
            assert _.upload_state()           == 'idle'                         # upload zone ready

        harness.teardown()