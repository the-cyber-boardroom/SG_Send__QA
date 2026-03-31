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

import pytest

from sg_send_qa.apis_for_sites.send_sgraph_ai.pages.Page__Send_SGraph_Ai__Upload import Page__Send_SGraph_Ai__Upload


class test_Page__Send_SGraph_Ai__Upload(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upload_page = Page__Send_SGraph_Ai__Upload()

    # @classmethod
    # def tearDownClass(cls):
    #     cls.upload_page.harness.teardown()          # todo: ok so this is why we where getting those errors

    def test_current_logic(self):
        with self.upload_page as _:
            _.current_logic()

    def test_debug_setup_chrome(self):
        with self.upload_page as _:
            _.debug_setup_chrome()

    @pytest.mark.skip("doesn't work when running with all tests") # todo: see below for the Async error
    def test_debug_inner_calls_of_setup(self):
        with self.upload_page as _:
            _.debug_inner_calls_of_setup()
            # >               raise Error(
            #                     """It looks like you are using Playwright Sync API inside the asyncio loop.
            #     Please use the Async API instead."""
            #                 )
            # E               playwright._impl._errors.Error: It looks like you are using Playwright Sync API inside the asyncio loop.
            # E               Please use the Async API instead.
            #
            # todo: we really need to figure out why this is happening, since this is the core reason we need to stop chrome between multiple class executions,
            #       and there are tons of cases where it would be a lot of efficient to keep the browser open
            #       for example in cases where we only want to setup once the access token

    def test_debug_start_api_server(self):
        with self.upload_page as _:
            _.debug_start_api_server()

    def test_debug_start_api_server__with_saved_state(self):
        with self.upload_page as _:
            _.debug_start_api_server__with_saved_state()

    def test_debug_inner_methods_of__start_api_server(self):
        with self.upload_page as _:
            _.debug_inner_methods_of__start_api_server()