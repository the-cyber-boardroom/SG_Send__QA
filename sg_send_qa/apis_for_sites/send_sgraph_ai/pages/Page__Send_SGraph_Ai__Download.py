# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — Download Page object
# High-level interface to the download page (combined-link and separate-key flows)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                     import SG_Send__Browser__Test_Harness
from sg_send_qa.browser.Schema__Browser_Test_Config                        import Schema__Browser_Test_Config
from sg_send_qa.browser.Schema__Download_Page                              import Schema__Download_Page


class Page__Send_SGraph_Ai__Download(Type_Safe):
    config  : Schema__Browser_Test_Config                                   # headless=True by default (CI safe)
    harness : SG_Send__Browser__Test_Harness = None                         # lifecycle owner — None until setup() is called
    sg_send = None                                                          # SG_Send__Browser__Pages — None until setup() is called

    # ═══════════════════════════════════════════════════════════════════════
    # Lifecycle
    # ═══════════════════════════════════════════════════════════════════════

    def setup(self):                                                        # start harness, set token, navigate to download page
        self.harness = SG_Send__Browser__Test_Harness(config=self.config)
        self.harness.setup()
        self.sg_send = self.harness.sg_send
        self.harness.set_access_token()
        self.sg_send.page__download()
        return self

    def teardown(self):                                                     # stop harness cleanly
        if self.harness:
            self.harness.teardown()
        return self

    # ═══════════════════════════════════════════════════════════════════════
    # Page actions
    # ═══════════════════════════════════════════════════════════════════════

    def download_combined(self, transfer_id: str, key_b64: str) -> Schema__Download_Page:   # open combined link, auto-decrypt, return state
        self.sg_send.page__download_with_hash(transfer_id=transfer_id, key_b64=key_b64)
        self.sg_send.wait_for_download_states(['complete', 'error'])
        return self.extract_state()

    def download_with_key(self, transfer_id: str, key: str) -> Schema__Download_Page:       # open by ID then enter key manually
        self.sg_send.page__download_with_id(transfer_id=transfer_id)
        self.sg_send.download__enter_key(key)
        self.sg_send.download__click_decrypt()
        return self.extract_state()

    def extract_state(self) -> Schema__Download_Page:                       # snapshot current download page state
        return self.sg_send.extract__download_page()
