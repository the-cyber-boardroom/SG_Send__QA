# from unittest                                                           import TestCase
# from sg_send_qa.browser.SG_Send__Browser__Pages                         import SG_Send__Browser__Pages
#
# class test_SG_Send__Browser__Pages__Download(TestCase):                         # Download page interactions
#     sg_send : SG_Send__Browser__Pages
#
#     @classmethod
#     def setUpClass(cls):
#         cls.sg_send = SG_Send__Browser__Pages()
#         cls.sg_send.qa_browser.headless = False
#
#     # ── Manual entry form ────────────────────────────────────────────────────
#
#     def test_download__manual_entry_form_visible(self):                         # entry form shows when no hash
#         self.sg_send.page__download()
#         self.sg_send.wait_for_page_ready()
#         self.sg_send.wait(1000)                                                 # let send-download render
#         is_visible = self.sg_send.raw_page().locator("#entry-input").is_visible(timeout=3000)
#         assert is_visible is True
#
#     def test_download__enter_bogus_token(self):                                 # bogus token shows error
#         self.sg_send.page__download()
#         self.sg_send.wait_for_page_ready()
#         self.sg_send.wait(1000)
#         self.sg_send.download__enter_manual_id("bogus-token-9999")
#         self.sg_send.download__submit_manual_entry()
#         text = self.sg_send.visible_text().lower()
#         assert any(kw in text for kw in ['not found', 'error', 'invalid'])
#
#     # ── Hash navigation ──────────────────────────────────────────────────────
#
#     def test_download__with_invalid_hash(self):                                 # invalid transfer ID shows error
#         self.sg_send.page__download_with_hash("nonexistent123", "fakekeyABCDEF")
#         self.sg_send.wait_for_page_ready()
#         self.sg_send.wait(3000)                                                 # let send-download fetch and render
#         text = self.sg_send.visible_text().lower()
#         assert 'not found' in text or 'error' in text or 'expired' in text
