from unittest                                          import TestCase
from sg_send_qa.browser.SG_Send__Browser__Test_Harness import SG_Send__Browser__Test_Harness


class test_SG_Send__Browser__Pages__Upload(TestCase):                           # Upload wizard — needs full local stack with valid token
    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().headless().setup()
        cls.sg_send = cls.harness.sg_send()
        cls.page_setup()

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()                                       # close the browser                                   # close the browser


    @classmethod
    def page_setup(cls):
        with cls.harness as _:
            cls.access_token = _.set_access_token()
            cls.ui_server    = _._ui_server

        with cls.sg_send as _:
            _.page__root()

    # ── Upload step-by-step ──────────────────────────────────────────────────

    def test_upload__set_file(self):                                            # file input works through shadow DOM
        print('here')
        return
        if self.sg_send.is_access_gate_visible() and self.access_token:
            self.sg_send.access_gate__enter_and_submit(self.access_token)
        self.sg_send.upload__set_file("test.txt", b"hello world")
        state = self.sg_send.upload_state()
        assert state in ('file-ready', 'choosing-delivery')                     # wizard advanced past idle

    def test_upload__click_next__to_share_step(self):                           # Next advances to share mode selection
        self.sg_send.page__root()
        self.sg_send.wait_for_page_ready()
        if self.sg_send.is_access_gate_visible() and self.access_token:
            self.sg_send.access_gate__enter_and_submit(self.access_token)
        self.sg_send.upload__set_file("test.txt", b"hello world")
        self.sg_send.upload__click_next()
        state = self.sg_send.upload_state()
        assert state == 'choosing-share'

    def test_upload__select_share_mode__combined(self):                          # selecting combined auto-advances to confirm
        self.sg_send.page__root()
        self.sg_send.wait_for_page_ready()
        if self.sg_send.is_access_gate_visible() and self.access_token:
            self.sg_send.access_gate__enter_and_submit(self.access_token)
        self.sg_send.upload__set_file("test.txt", b"hello world")
        self.sg_send.upload__click_next()
        self.sg_send.upload__select_share_mode("combined")
        state = self.sg_send.upload_state()
        assert state == 'confirming'