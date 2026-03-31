# todo I place this in this tests/qa/apis_for_sites folder because
#     - this needs a live website (first locally, but we should also support the multiple live sites)
#     - so it is not an unit test,
#     - could be an integration test
#     - but since we are going to also be adding a lot more sites here, and this is one of the set of tests that
#       the qa team will be executing in order to make the decision to go live or not with a nre release
#       this 'qa' folder felt right
#     - the idea is then to use these classes inside the v030 folder which should simplify that code quite a bit
#     - we might actually move these also to an v030 folder (or v03x or v04x) , since some of these tests will be version specific
#       which will be very relevant when we start to have test suites that need to run again multiple IFD versions
#
#
# todo first refactor that I'm going to do is the code in def _upload_with_simple_token(self, shots, filename="token-test.txt"):
#      from the tests/qa/v030/p0__friendly_token/test__friendly_token.py (see notes on that file, here is just the code)
#
#
#     def _upload_with_simple_token(self, shots, filename="token-test.txt"):
#         """Upload a file with Simple Token mode and return the friendly token string."""
#         self.sg_send.page__root()
#         self.sg_send.upload__set_file(filename, SAMPLE_CONTENT.encode())

#         shots.capture(self.sg_send.raw_page(), "01_file_selected", "File selected (delivery step active)")
#
#         self.sg_send.upload__click_next()
#         self.sg_send.upload__select_share_mode("token")
#         shots.capture(self.sg_send.raw_page(), "02_simple_token_selected", "Simple Token selected")
#         self.sg_send.upload__click_next()
#         self.sg_send.upload__wait_for_complete()
#         shots.capture(self.sg_send.raw_page(), "03_upload_complete", "Upload complete")
#
#         return self.sg_send.upload__get_friendly_token()
from unittest                                                                    import TestCase
from sg_send_qa.apis_for_sites.send_sgraph_ai.pages.Page__Send_SGraph_Ai__Upload import Page__Send_SGraph_Ai__Upload


class test_Page__Send_SGraph_Ai__Upload(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upload_page = Page__Send_SGraph_Ai__Upload()


    def test_current_logic(self):
        with self.upload_page as _:
            _.current_logic()

    def test_debug_setup_chrome(self):
        with self.upload_page as _:
            _.debug_setup_chrome()

    # todo: interesting, when I run the test in the 2nd test method
    #       I get this error (on the 2nd method)
    #     def test_debug_setup_chrome(self):
#         with self.upload_page as _:
# >           _.debug_setup_chrome()
#
# modules/SG_Send__QA/tests/qa/apis_for_sites/send_sgraph_ai/pages/test_Page__Send_SGraph_Ai__Upload.py:48:
# _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
# modules/SG_Send__QA/sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Upload.py:54: in debug_setup_chrome
#     self.harness.headless(False).setup()
# modules/SG_Send__QA/sg_send_qa/browser/SG_Send__Browser__Test_Harness.py:54: in setup
#     self._start_ui_server(saved_state)
# modules/SG_Send__QA/sg_send_qa/browser/SG_Send__Browser__Test_Harness.py:168: in _start_ui_server
#     self.ui_server.__enter__()
# ../../../Library/Caches/pypoetry/virtualenvs/sgraph-ai-app-send-wR0WO4Cj-py3.12/lib/python3.12/site-packages/osbot_utils/testing/Temp_Web_Server.py:24: in __enter__
#     self.start()
# ../../../Library/Caches/pypoetry/virtualenvs/sgraph-ai-app-send-wR0WO4Cj-py3.12/lib/python3.12/site-packages/osbot_utils/testing/Temp_Web_Server.py:74: in start
#     self.server        = ThreadingHTTPServer((self.host, self.port), handler_config)
#                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# /opt/homebrew/Cellar/python@3.12/3.12.8/Frameworks/Python.framework/Versions/3.12/lib/python3.12/socketserver.py:457: in __init__
#     self.server_bind()
# /opt/homebrew/Cellar/python@3.12/3.12.8/Frameworks/Python.framework/Versions/3.12/lib/python3.12/http/server.py:136: in server_bind
#     socketserver.TCPServer.server_bind(self)
# _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
#
# self = <http.server.ThreadingHTTPServer object at 0x1090d8d10>
#
#     def server_bind(self):
#         """Called by constructor to bind the socket.
#
#         May be overridden.
#
#         """
#         if self.allow_reuse_address and hasattr(socket, "SO_REUSEADDR"):
#             self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         if self.allow_reuse_port and hasattr(socket, "SO_REUSEPORT"):
#             self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# >       self.socket.bind(self.server_address)
# E       OSError: [Errno 48] Address already in use


