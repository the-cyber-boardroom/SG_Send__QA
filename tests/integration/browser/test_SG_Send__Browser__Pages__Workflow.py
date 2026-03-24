# from unittest                                                           import TestCase
# from sg_send_qa.browser.SG_Send__Browser__Pages                         import SG_Send__Browser__Pages
#
# class test_SG_Send__Browser__Pages__Workflow(TestCase):                         # Full workflow tests — need local stack + valid token
#     sg_send      : SG_Send__Browser__Pages
#     access_token : str
#
#     @classmethod
#     def setUpClass(cls):
#         cls.sg_send = SG_Send__Browser__Pages()
#         cls.sg_send.qa_browser.headless = False
#         # To run these tests, set the access token for your local QA server:
#         cls.access_token = ""                                                   # set this to your local token
#
#     def _skip_if_no_token(self):
#         if not self.access_token:
#             self.skipTest("No access token — set cls.access_token for workflow tests")
#
#     # ── Combined link workflow ───────────────────────────────────────────────
#
#     def test_workflow__upload_combined(self):                                    # full upload → get combined link
#         self._skip_if_no_token()
#         link = self.sg_send.workflow__upload_combined(
#             token         = self.access_token       ,
#             filename      = "workflow-test.txt"      ,
#             content_bytes = b"Workflow test content." ,
#         )
#         assert link                                                             # link is not empty
#         assert 'http' in link or '/' in link                                    # looks like a URL
#
#     def test_workflow__upload_friendly_token(self):                              # full upload → get friendly token
#         self._skip_if_no_token()
#         token = self.sg_send.workflow__upload_friendly_token(
#             token         = self.access_token                     ,
#             filename      = "token-test.txt"                       ,
#             content_bytes = b"Friendly token workflow test content.",
#         )
#         assert token                                                            # token is not empty
#         parts = token.split("-")
#         assert len(parts) == 3                                                  # word-word-NNNN format
#
#     def test_workflow__upload_and_browse(self):                                  # upload combined, then open in browse view
#         self._skip_if_no_token()
#         link = self.sg_send.workflow__upload_combined(
#             token         = self.access_token     ,
#             filename      = "browse-test.txt"      ,
#             content_bytes = b"Browse workflow test.",
#         )
#         assert link
#         # extract hash from the combined link
#         if '#' in link:
#             hash_part = link.split('#', 1)[1]
#             parts     = hash_part.split('/', 1)
#             if len(parts) == 2:
#                 self.sg_send.page__browse_with_hash(parts[0], parts[1])
#                 self.sg_send.wait(3000)                                         # let decrypt complete
#                 text = self.sg_send.visible_text()
#                 assert 'Browse workflow test.' in text or 'browse-test.txt' in text