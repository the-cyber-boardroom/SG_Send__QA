# from unittest                                                           import TestCase
# from sg_send_qa.browser.SG_Send__Browser__Pages                         import SG_Send__Browser__Pages
#
# class test_SG_Send__Browser__Pages__Access_Gate(TestCase):                      # Access gate interaction
#     sg_send : SG_Send__Browser__Pages
#
#     @classmethod
#     def setUpClass(cls):
#         cls.sg_send = SG_Send__Browser__Pages()
#         cls.sg_send.qa_browser.headless = False
#
#     # ── Access gate ──────────────────────────────────────────────────────────
#
#     def test_access_gate__enter_token(self):                                    # can type into the token input
#         self.sg_send.page__root()
#         self.sg_send.wait_for_page_ready()
#         self.sg_send.access_gate__enter_token("test-token-12345")
#         value = self.sg_send.js(
#             "document.querySelector('#access-token-input')?.value"
#         )
#         assert value == "test-token-12345"
#
#     def test_access_gate__wrong_token_shows_error(self):                        # wrong token shows error feedback
#         self.sg_send.page__root()
#         self.sg_send.wait_for_page_ready()
#         self.sg_send.access_gate__enter_and_submit("wrong-token-xxxxx")
#         text = self.sg_send.visible_text().lower()
#         gate_still_visible = self.sg_send.is_access_gate_visible()
#         assert 'invalid' in text or 'error' in text or gate_still_visible       # error shown or gate remains
#
#
