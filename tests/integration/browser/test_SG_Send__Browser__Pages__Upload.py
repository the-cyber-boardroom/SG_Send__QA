# from unittest                                                           import TestCase
# from sg_send_qa.browser.SG_Send__Browser__Pages                         import SG_Send__Browser__Pages
#
#
# class test_SG_Send__Browser__Pages__Upload(TestCase):                           # Upload wizard — needs full local stack with valid token
#     sg_send      : SG_Send__Browser__Pages
#     access_token : str
#
#     @classmethod
#     def setUpClass(cls):
#         cls.sg_send = SG_Send__Browser__Pages()
#         cls.sg_send.qa_browser.headless = False
#         cls.access_token = cls._get_access_token()
#
#     @classmethod
#     def _get_access_token(cls):                                                 # get access token from the QA server test objects
#         try:
#             from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import (
#                 setup__send_user_lambda__test_server,
#             )
#             # note: this assumes the test server is already running on port 10062
#             # if not, tests in this class will fail at the access gate
#             return ""                                                           # empty = no gate or gate bypassed
#         except ImportError:
#             return ""
#
#     # ── Upload step-by-step ──────────────────────────────────────────────────
#
#     def test_upload__set_file(self):                                            # file input works through shadow DOM
#         self.sg_send.page__root()
#         self.sg_send.wait_for_page_ready()
#         if self.sg_send.is_access_gate_visible() and self.access_token:
#             self.sg_send.access_gate__enter_and_submit(self.access_token)
#         self.sg_send.upload__set_file("test.txt", b"hello world")
#         state = self.sg_send.upload_state()
#         assert state in ('file-ready', 'choosing-delivery')                     # wizard advanced past idle
#
#     def test_upload__click_next__to_share_step(self):                           # Next advances to share mode selection
#         self.sg_send.page__root()
#         self.sg_send.wait_for_page_ready()
#         if self.sg_send.is_access_gate_visible() and self.access_token:
#             self.sg_send.access_gate__enter_and_submit(self.access_token)
#         self.sg_send.upload__set_file("test.txt", b"hello world")
#         self.sg_send.upload__click_next()
#         state = self.sg_send.upload_state()
#         assert state == 'choosing-share'
#
#     def test_upload__select_share_mode__combined(self):                          # selecting combined auto-advances to confirm
#         self.sg_send.page__root()
#         self.sg_send.wait_for_page_ready()
#         if self.sg_send.is_access_gate_visible() and self.access_token:
#             self.sg_send.access_gate__enter_and_submit(self.access_token)
#         self.sg_send.upload__set_file("test.txt", b"hello world")
#         self.sg_send.upload__click_next()
#         self.sg_send.upload__select_share_mode("combined")
#         state = self.sg_send.upload_state()
#         assert state == 'confirming'