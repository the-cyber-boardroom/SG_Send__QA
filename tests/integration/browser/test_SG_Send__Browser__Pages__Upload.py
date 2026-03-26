from unittest                                           import TestCase
from osbot_utils.testing.Stderr                         import Stderr
from osbot_playwright.playwright.api.Playwright_Page    import Playwright_Page
from sg_send_qa.browser.SG_Send__Browser__Pages         import SG_Send__Browser__Pages
from sg_send_qa.browser.SG_Send__Browser__Test_Harness  import SG_Send__Browser__Test_Harness
from sg_send_qa.state_machines.State_Machine__Upload    import upload_state_machine
from sg_send_qa.state_machines.State_Machine__Utils     import State_Machine__Utils

SAMPLE_CONTENT  = "Hello from SG/Send QA — upload wizard test."
SAMPLE_FILENAME = "qa-upload-test.txt"

class test_SG_Send__Browser__Pages__Upload(TestCase):                           # Upload wizard — needs full local stack with valid token
    @classmethod
    def setUpClass(cls):
        cls.harness     = SG_Send__Browser__Test_Harness().headless(True).setup()
        cls.sg_send     = cls.harness.sg_send
        cls.upload_sm   = upload_state_machine()
        cls.sm_utils    = State_Machine__Utils()
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
            cls.ui_server    = _.ui_server

    # ── Upload step-by-step ──────────────────────────────────────────────────

    def test__01__upload__set_file(self):                                            # file input works through shadow DOM
        with self.sg_send.page() as _:
            assert type(_) is Playwright_Page

        with self.sg_send as _:
            assert type(_) is SG_Send__Browser__Pages
            _.page__root()
            state_before = 'idle'
            _.upload__set_file(SAMPLE_FILENAME, SAMPLE_CONTENT.encode())
            state_after = _.upload_state()
            assert state_after in ('file-ready', 'choosing-delivery')               # wizard advanced past idle
            assert self.sm_utils.validate_transition(self.upload_sm,                # graph edge validated
                                                     state_before, state_after)

    def test__02__upload__click_next__to_share_step(self):                           # Next advances to share mode selection
        state_before = self.sg_send.upload_state()
        self.sg_send.upload__click_next()
        state_after = self.sg_send.upload_state()
        assert state_after == 'choosing-share'
        assert self.sm_utils.validate_transition(self.upload_sm,                    # graph edge validated
                                                 state_before, state_after)

    def test__03__upload__select_share_mode__simple(self):                          # selecting combined auto-advances to confirm
        state_before = self.sg_send.upload_state()
        self.sg_send.upload__select_share_mode("token")
        state_after = self.sg_send.upload_state()
        assert state_after == 'confirming'
        assert self.sm_utils.validate_transition(self.upload_sm,                    # graph edge validated
                                                 state_before, state_after)

    # def test__03__upload__select_share_mode__combined(self):                          # selecting combined auto-advances to confirm
    #     self.sg_send.upload__select_share_mode("combined")
    #     assert self.sg_send.upload_state() == 'confirming'

    def test__04__upload__click_encrypt_and_upload(self):                             # Encrypt & Upload starts the pipeline
        self.sg_send.upload__click_next()                                            # in confirming state, button says "Encrypt & Upload"
        self.sg_send.upload__wait_for_complete()                                     # wait for: encrypting → creating → uploading → completing → complete
        assert self.sg_send.upload_state() == 'complete'

    def test__05__upload__get_simple_token(self):                                   # extract combined link from done step
        simple_token = self.sg_send.upload__get_friendly_token()                    # todo: these upload__get_friendly_token methods need to be moved to a class with logic specific to this upload page
        assert len(simple_token.split("-")) == 3
        # todo  add way to percist this token

    # def test__05__upload__get_combined_link(self):                                   # extract combined link from done step
    #     #link = self.sg_send.upload__get_combined_link()
    #     simple_token = self.sg_send.upload__get_friendly_token()                    # todo: these upload__get_friendly_token methods need to be moved to a class with logic specific to this upload page
    #     assert len(simple_token.split("-")) == 3

    # the test bellow need either open in a new window, or we need a way to keep the state of this page
    # def test__06__combined_link__format(self):                                       # verify #transferId/base64key format
    #     link      = self.__class__.combined_link
    #     hash_part = link.split('#', 1)[1]
    #     parts     = hash_part.split('/', 1)
    #     assert len(parts)    == 2                                                    # two parts: id and key
    #     assert len(parts[0]) >= 8                                                    # transfer ID is at least 8 chars
    #     assert len(parts[1]) >  0                                                    # key is not empty
    #     self.__class__.transfer_id = parts[0]
    #     self.__class__.key_b64     = parts[1]
    #
    # def test__07__browse__decrypted_content(self):                                   # open combined link in browse view, verify decryption
    #     tid = self.__class__.transfer_id
    #     key = self.__class__.key_b64
    #     with self.sg_send as _:
    #         _.page__browse_with_hash(tid, key)
    #         _.wait(3000)                                                             # allow JS fetch + decrypt + render
    #         text = _.visible_text()
    #         assert SAMPLE_CONTENT in text                                            # decrypted content visible
    #
    # def test__08__browse__filename_visible(self):                                    # filename extracted from SGMETA envelope
    #     text = self.sg_send.visible_text()
    #     assert SAMPLE_FILENAME in text                                               # filename shown in viewer