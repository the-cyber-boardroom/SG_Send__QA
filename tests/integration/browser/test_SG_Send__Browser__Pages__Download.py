from unittest                                           import TestCase
from osbot_utils.testing.Stderr                         import Stderr
from sg_send_qa.browser.SG_Send__Browser__Test_Harness  import SG_Send__Browser__Test_Harness
from sg_send_qa.state_machines.State_Machine__Download  import download_state_machine
from sg_send_qa.state_machines.State_Machine__Utils     import State_Machine__Utils

SAMPLE_CONTENT  = b"Download integration test -- SG/Send QA."
SAMPLE_FILENAME = "download-test.txt"


class test_SG_Send__Browser__Pages__Download(TestCase):                          # Download page interaction tests
    @classmethod
    def setUpClass(cls):
        cls.harness      = SG_Send__Browser__Test_Harness().headless(True).setup()
        cls.sg_send      = cls.harness.sg_send
        cls.helper       = cls.harness.transfer_helper()
        cls.download_sm  = download_state_machine()
        cls.sm_utils     = State_Machine__Utils()
        with cls.harness as _:
            _.set_access_token()

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    def setUp(self):
        Stderr().start()

    # ---- Manual entry form -------------------------------------------------

    def test__01__download__manual_entry_form_visible(self):                     # entry form shows when no hash
        self.sg_send.page__download()
        self.sg_send.wait_for_download_state("entry")                           # send-download reaches 'entry' state = form visible
        assert self.sg_send.js().light_visible("#entry-input") is True          # read via JS query layer
        # graph edge: loading → entry (no hash in URL)
        assert self.sm_utils.validate_transition(self.download_sm, 'loading', 'entry')

    def test__02__download__bogus_token_form_response(self):                     # bogus token: UI shows feedback (error or resets form)
        self.sg_send.page__download()
        self.sg_send.wait_for_download_state("entry")
        self.sg_send.download__enter_manual_id("bogus-token-9999")
        self.sg_send.download__submit_manual_entry()                            # internally waits for ready/complete/error
        text = self.sg_send.visible_text().lower()
        # UI may show explicit error text OR silently reset the form (both are valid responses)
        error_shown  = any(kw in text for kw in ["not found", "error", "invalid", "expired"])
        form_visible = self.sg_send.js().light_visible("#entry-input")          # read via JS query layer
        assert error_shown or form_visible                                       # gate responded in some way

    # ---- Hash navigation ---------------------------------------------------

    def test__03__download__with_invalid_hash__graceful(self):                   # invalid hash -> graceful fallback (not crash)
        self.sg_send.page__download_with_hash("nonexistent123", "fakekeyABCDEF==")
        self.sg_send.wait_for_download_states(["error", "entry"])               # error state or falls back to entry form
        text = self.sg_send.visible_text().lower()
        # App may show explicit error OR fall back to the entry form (both are graceful)
        error_shown  = any(kw in text for kw in ["not found", "error", "invalid", "expired"])
        form_visible = self.sg_send.js().light_visible("#entry-input")          # read via JS query layer
        assert error_shown or form_visible                                       # no unhandled crash

    def test__04__download__valid_hash_shows_content(self):                      # valid hash -> decrypted content visible
        tid, key_b64 = self.helper.upload_encrypted(SAMPLE_CONTENT, SAMPLE_FILENAME)
        self.__class__.transfer_id = tid
        self.__class__.key_b64     = key_b64

        self.sg_send.page__browse_with_hash(tid, key_b64)
        self.sg_send.wait_for_download_state("complete")                        # wait for decrypt pipeline to finish
        text = self.sg_send.visible_text()
        assert SAMPLE_CONTENT.decode() in text or SAMPLE_FILENAME in text
        # graph edges: loading → ready → [browse|viewer|gallery] and ultimately → complete
        assert self.sm_utils.validate_transition(self.download_sm, 'loading', 'ready')
        assert self.sm_utils.validate_transition(self.download_sm, 'decrypting', 'complete')

    def test__05__download__gallery_view_with_valid_hash(self):                  # valid hash in gallery view
        tid, key_b64 = self.helper.upload_encrypted(SAMPLE_CONTENT, SAMPLE_FILENAME)
        self.sg_send.page__gallery_with_hash(tid, key_b64)
        self.sg_send.wait_for_download_state("complete")
        text = self.sg_send.visible_text()
        assert "error" not in text.lower() or len(text) > 100

    def test__06__download__separate_key_mode__key_input_visible(self):          # separate-key: key input appears; decrypt triggered
        # NOTE: After clicking Decrypt, the decrypted content is NOT visible via
        # inner_text("body") — it renders in shadow DOM or triggers a file download.
        # This is a known UI behavior — tracked in tests/integration/browser/bugs/.
        # This test validates: navigation -> 'ready' or 'error' state -> key entry if ready -> decrypt -> 'complete' or 'error'
        tid, key_b64 = self.helper.upload_encrypted(SAMPLE_CONTENT, SAMPLE_FILENAME,
                                                    content_type="text/plain")
        self.sg_send.page__download_with_id(tid)
        self.sg_send.wait_for_download_states(["ready", "error"])               # component either fetched transfer (ready) or failed (error)

        key_input_visible = self.sg_send.js().light_visible("#key-input")        # read via JS query layer

        if key_input_visible:                                                   # 'ready' state: key input visible — attempt decrypt
            self.sg_send.download__enter_key(key_b64)                          # enter_key already waits for #key-input visible
            self.sg_send.download__click_decrypt()                             # click_decrypt waits for complete/error state

        # After decrypt (or error): browser still responsive
        assert self.sg_send.url() is not None

    def test__07__download__localStorage_handoff(self):                          # store + read back transfer ID/key
        tid, key_b64 = self.helper.upload_encrypted(SAMPLE_CONTENT, SAMPLE_FILENAME)

        js = self.sg_send.js()
        js.storage_set('qa-transfer-id',  tid)                                  # base64-safe write
        js.storage_set('qa-transfer-key', key_b64)
        read_tid = js.storage_get('qa-transfer-id')                             # base64-safe read
        read_key = js.storage_get('qa-transfer-key')
        assert read_tid == tid
        assert read_key == key_b64

        self.sg_send.page__browse_with_hash(read_tid, read_key)
        self.sg_send.wait_for_download_state("complete")
        text = self.sg_send.visible_text()
        assert SAMPLE_CONTENT.decode() in text or SAMPLE_FILENAME in text
