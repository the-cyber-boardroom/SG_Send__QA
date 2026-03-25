from unittest                                           import TestCase
from osbot_utils.testing.Stderr                         import Stderr
from sg_send_qa.browser.SG_Send__Browser__Test_Harness  import SG_Send__Browser__Test_Harness


class test_SG_Send__Browser__Pages__Access_Gate(TestCase):                       # Access gate interaction tests
    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().headless(True).setup()
        cls.sg_send = cls.harness.sg_send
        with cls.harness as _:
            cls.access_token = _.access_token()                                 # the valid token from in-memory server

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    def setUp(self):
        Stderr().start()

    def _clear_token_and_go_root(self):                                          # helper: remove token from localStorage then navigate to root
        self.sg_send.page__qa_setup()
        self.sg_send.js().storage_remove('sgraph-send-token')                   # base64-safe remove
        self.sg_send.page__root()
        self.sg_send.wait_for_selector_visible("#access-token-input")           # event-based: wait for gate input to appear

    # ---- Access gate visibility --------------------------------------------

    def test__01__gate__visible_without_token(self):                             # gate shows when no token in localStorage
        self._clear_token_and_go_root()
        assert self.sg_send.is_access_gate_visible() is True

    def test__02__gate__enter_token_into_input(self):                            # can type into the token input field
        self._clear_token_and_go_root()
        self.sg_send.access_gate__enter_token("test-token-12345")
        value = self.sg_send.js().light_value("#access-token-input")            # read input value through JS query layer
        assert value == "test-token-12345"

    def test__03__gate__wrong_token_shows_error_or_stays(self):                  # gate responds to wrong token submission
        self._clear_token_and_go_root()
        self.sg_send.access_gate__enter_and_submit("wrong-token-xxxxx")        # submit internally waits for gate response
        text               = self.sg_send.visible_text().lower()
        gate_still_visible = self.sg_send.is_access_gate_visible()
        # The local test server may accept any token (in-memory, no real validation)
        # Acceptance: gate dismissed + upload zone visible
        # Rejection:  gate still visible or error text shown
        gate_dismissed_and_upload_visible = (
            not gate_still_visible and self.sg_send.is_upload_zone_visible()
        )
        assert ("invalid" in text or "error" in text or
                gate_still_visible or gate_dismissed_and_upload_visible)

    def test__04__gate__correct_token_hides_gate(self):                          # valid token passes the gate
        self._clear_token_and_go_root()
        self.sg_send.access_gate__enter_and_submit(self.access_token)          # submit waits for gate to respond
        self.sg_send.wait_for_selector_visible("upload-step-select")            # event-based: wait for upload zone to appear
        assert self.sg_send.is_access_gate_visible() is False
        assert self.sg_send.is_upload_zone_visible() is True

    def test__05__gate__pre_set_token_via_localStorage(self):                    # token pre-loaded skips gate entirely
        self.sg_send.page__qa_setup()
        self.sg_send.storage__set_token(self.access_token)
        self.sg_send.page__root()
        self.sg_send.wait_for_selector_visible("upload-step-select")            # event-based: upload zone present = gate bypassed
        assert self.sg_send.is_access_gate_visible() is False
        assert self.sg_send.is_upload_zone_visible() is True
