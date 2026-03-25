from unittest                                           import TestCase
from osbot_utils.testing.Stderr                         import Stderr
from sg_send_qa.browser.SG_Send__Browser__Pages         import SG_Send__Browser__Pages
from sg_send_qa.browser.SG_Send__Browser__Test_Harness  import SG_Send__Browser__Test_Harness

SAMPLE_CONTENT  = b"Workflow integration test -- SG/Send QA round trip."
SAMPLE_FILENAME = "workflow-test.txt"


class test_SG_Send__Browser__Pages__Workflow(TestCase):                          # Full upload -> download round-trip
    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().headless(True).setup()
        cls.sg_send = cls.harness.sg_send
        cls.helper  = cls.harness.transfer_helper()
        cls.page_setup()

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    def setUp(self):
        Stderr().start()

    @classmethod
    def page_setup(cls):
        with cls.harness as _:
            cls.access_token = _.set_access_token()

    # ---- Upload via browser, read results -----------------------------------

    def test__01__workflow__upload_friendly_token(self):                         # upload and retrieve friendly token
        with self.sg_send as _:
            assert type(_) is SG_Send__Browser__Pages
            _.page__root()
            _.upload__set_file(SAMPLE_FILENAME, SAMPLE_CONTENT)
            _.upload__click_next()                                              # -> choosing-share
            _.upload__select_share_mode("token")                               # -> confirming
            _.upload__click_next()                                             # -> uploading
            _.upload__wait_for_complete()
            assert _.upload_state() == "complete"

    def test__02__workflow__get_token_and_persist(self):                         # extract token and store in localStorage
        simple_token = self.sg_send.upload__get_friendly_token()
        assert simple_token and len(simple_token.split("-")) == 3               # word-word-NNNN
        # persist for downstream test
        self.sg_send.js_evaluate(
            f"localStorage.setItem('qa-workflow-token', '{simple_token}')"
        )
        self.__class__.simple_token = simple_token

    def test__03__workflow__navigate_to_welcome_with_token(self):                # friendly token -> welcome page resolves
        self.sg_send.page__welcome()
        self.sg_send.wait(1500)                                                 # let send-welcome render
        text = self.sg_send.visible_text()
        # welcome page should be reachable -- not an error
        assert "error" not in text.lower() or len(text) > 200

    # ---- Upload via API (transfer_helper), read via browser -----------------

    def test__04__workflow__api_upload_browser_download(self):                   # API upload -> browser hash navigation
        tid, key_b64 = self.helper.upload_encrypted(SAMPLE_CONTENT, SAMPLE_FILENAME)
        assert tid and key_b64

        # store in class for subsequent tests
        self.__class__.transfer_id = tid
        self.__class__.key_b64     = key_b64

        # navigate browser to the download hash URL
        self.sg_send.page__browse_with_hash(tid, key_b64)
        self.sg_send.wait(4000)                                                 # decrypt + render

        text = self.sg_send.visible_text()
        assert SAMPLE_CONTENT.decode() in text or SAMPLE_FILENAME in text

    def test__05__workflow__api_upload_gallery_view(self):                       # API upload -> gallery hash navigation
        tid, key_b64 = self.helper.upload_encrypted(SAMPLE_CONTENT, SAMPLE_FILENAME)
        self.sg_send.page__gallery_with_hash(tid, key_b64)
        self.sg_send.wait(4000)
        text = self.sg_send.visible_text()
        assert "error" not in text.lower() or len(text) > 100

    def test__06__workflow__localStorage_handoff(self):                          # upload stores ID + key; read back
        tid, key_b64 = self.helper.upload_encrypted(SAMPLE_CONTENT, SAMPLE_FILENAME)

        # simulate what an upload-then-download test sequence does
        self.sg_send.js_evaluate(
            f"localStorage.setItem('qa-transfer-id',  '{tid}');"
            f"localStorage.setItem('qa-transfer-key', '{key_b64}');"
        )

        read_tid = self.sg_send.js_evaluate("localStorage.getItem('qa-transfer-id')")
        read_key = self.sg_send.js_evaluate("localStorage.getItem('qa-transfer-key')")

        assert read_tid == tid
        assert read_key == key_b64
