from unittest                                          import TestCase
from sg_send_qa.browser.SG_Send__Browser__Test_Harness import SG_Send__Browser__Test_Harness


class test_SG_Send__Browser__Pages__State(TestCase):                            # Page state queries

    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().setup()
        cls.sg_send = cls.harness.sg_send()
        cls.page_setup()

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()                                       # close the browser


    @classmethod
    def page_setup(cls):
        cls.access_token = cls.harness.access_token()
        cls.ui_server    = cls.harness._ui_server
        with cls.sg_send as _:
            _.page__qa_setup()
            _.storage__clear()          # make sure it is clear
            _.page__root()

    # ── Check page set ───────────────────────────────────────────────────────
    def test__page_setup(self):
        with self.sg_send.page() as _:
            assert _.url() == f'http://localhost:{self.ui_server.port}/en-gb/'


    # ── Check pages when storage is empty ───────────────────────────────────────────────────────


    def test_wait_for_page_ready(self):                                         # body[data-ready] appears after init
        ready = self.sg_send.js_evaluate("document.body.getAttribute('data-ready')")     # confirm that .wait_for_page_ready() is not needed
        assert ready == 'true'

    def test_visible_text__no_script_content(self):                             # inner_text excludes <script> tags
        text = self.sg_send.visible_text()
        assert 'Enter your access token to start sending files' in text         # visible header text
        assert 'window.fetch'                                   not in text     # script content not included

    def test_is_access_gate_visible__on_root(self):                             # access gate shows on upload page
        assert self.sg_send.is_access_gate_visible() is True


    # def test_url__after_navigation(self):                                       # URL reflects current page
    #     self.sg_send.page__gallery()
    #     assert 'gallery' in self.sg_send.url()

    def test_js__document_title(self):                                          # JS eval works
        title = self.sg_send.js_evaluate('document.title')
        assert 'SG/Send' in title