# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — Browse Page object
# High-level interface to the browse view (combined-link / hash-fragment flow)
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                     import SG_Send__Browser__Test_Harness
from sg_send_qa.browser.Schema__Browser_Test_Config                        import Schema__Browser_Test_Config
from sg_send_qa.browser.Schema__Browse_Page                                import Schema__Browse_Page


class Page__Send_SGraph_Ai__Browse(Type_Safe):
    config  : Schema__Browser_Test_Config                                   # headless=True by default (CI safe)
    harness : SG_Send__Browser__Test_Harness = None                         # lifecycle owner — None until setup() is called
    sg_send = None                                                          # SG_Send__Browser__Pages — None until setup() is called

    # ═══════════════════════════════════════════════════════════════════════
    # Lifecycle
    # ═══════════════════════════════════════════════════════════════════════

    def setup(self):                                                        # start harness, set token, navigate to browse page
        self.harness = SG_Send__Browser__Test_Harness(config=self.config)
        self.harness.setup()
        self.sg_send = self.harness.sg_send
        self.harness.set_access_token()
        self.sg_send.page__browse()
        return self

    def teardown(self):                                                     # stop harness cleanly
        if self.harness:
            self.harness.teardown()
        return self

    # ═══════════════════════════════════════════════════════════════════════
    # Page actions
    # ═══════════════════════════════════════════════════════════════════════

    def browse_tree(self, transfer_id: str, key_b64: str) -> Schema__Browse_Page:   # open browse page with hash, return state
        self.sg_send.page__browse_with_hash(transfer_id=transfer_id, key_b64=key_b64)
        return self.extract_state()

    def extract_state(self) -> Schema__Browse_Page:                         # snapshot current browse page state
        return self.sg_send.extract__browse_page()
