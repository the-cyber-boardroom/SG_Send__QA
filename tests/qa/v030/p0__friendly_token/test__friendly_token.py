"""UC-03: Friendly Token — Simple Token share mode (P0).

This was a P0 bug — critical to test.

Flow:
  1. Upload a file with Simple Token share mode
  2. Capture the friendly token (word-word-NNNN format)
  3. Open a new tab to /en-gb/browse/#<friendly-token>
  4. Verify the token resolves and content decrypts
"""
import re
from pathlib                                                    import Path
from unittest                                                   import TestCase
import pytest
from sg_send_qa.browser.SG_Send__Browser__Test_Harness         import SG_Send__Browser__Test_Harness
from sg_send_qa.utils.QA_Screenshot_Capture                    import ScreenshotCapture

pytestmark = pytest.mark.p0

SAMPLE_CONTENT = "Friendly token test — UC-03."
TOKEN_PATTERN  = re.compile(r"\b[a-z]+-[a-z]+-\d{4}\b")
# todo: change how this path is captured (so that it is not hardcoded like this
_BASE  = Path(__file__).parent.parent.parent.parent.parent / "sg_send_qa__site" / "pages" / "use-cases"
_GROUP = "02-upload-share"          # todo: this is not where these values should be defined
_UC    = "friendly_token"


class test_Friendly_Token(TestCase):        # Validate the Simple Token (friendly token) share mode end-to-end.

    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().headless(False).setup()
        cls.sg_send = cls.harness.sg_send
        cls.harness.set_access_token()              # todo: we need a much better way to handle this (specially when we are reusing the browser)

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    def _shots(self, method_name, method_doc=""):
        shots_dir = _BASE / _GROUP / _UC / "screenshots"
        return ScreenshotCapture(
            use_case    = _UC,
            module_name = "test__friendly_token",
            module_doc  = __doc__,
            method_name = method_name,
            method_doc  = method_doc,
            shots_dir   = shots_dir,
        )

    # todo: this is a good example of util class that should not exist in this class
    #       - this should be in Page specific class (in this case related to the Upload workflow)
    def _upload_with_simple_token(self, shots, filename="token-test.txt"):
        """Upload a file with Simple Token mode and return the friendly token string."""
        self.sg_send.page__root()
        self.sg_send.upload__set_file(filename, SAMPLE_CONTENT.encode())
        # todo: util class like this should not take screenshots, since the point here is to return a valid simple token
        #       since we want to capture the simple token screenshot, we should capture it on the test that checks that
        shots.capture(self.sg_send.raw_page(), "01_file_selected", "File selected (delivery step active)")          # todo: note how we keep calling "shots.capture(self.sg_send.raw_page()," all the time, this is a good example of code that needs to be refactored since it costs in context reading (for human and LLM)

        self.sg_send.upload__click_next()                               # todo: upload__click_next needs to be refactored to a page class that knows where we are  and that uses a 'next()' method
        self.sg_send.upload__select_share_mode("token")
        shots.capture(self.sg_send.raw_page(), "02_simple_token_selected", "Simple Token selected")
        # todo: note that we we didn't capture here if we are actually on tehe correct page
        self.sg_send.upload__click_next()                               # todo: good example of methods that can actually we doing actions that we don't know about (since which next is this?)
        self.sg_send.upload__wait_for_complete()                        # todo: need better way to do this, since what does 'complete' mean?
        shots.capture(self.sg_send.raw_page(), "03_upload_complete", "Upload complete")

        return self.sg_send.upload__get_friendly_token()                # todo: how do we know if we got a valid token here
        # todo: amongst the reasons we really need to have these Page clases is that , they become important tests to run first
        #       since for example, if there was a change in the code that made this _upload_with_simple_token class not return valid token (even if a well formed one , but not valid)
        #           we would have multiple tests in this current class that would fail, with failures that had nothing to do with that that test was testing
        #           for example the check download action would fail, but not becasue there is something wrong with the download code/workflow
        #           this is also the tests for these Page classes become important ones to run/execute first, since if any of them fail then there is no point of running any other tests

    def test__01__friendly_token_upload_and_resolve(self):      # Upload with Simple Token mode, then resolve the friendly token in a new tab.
        # todo: we need a way to capture all screenshots in memory first (during a test like this, and then decide in the end if we need to test it)
        #       also this is a good example of a test that should be levarging domain classes (i.e an Upload Page class)

        shots         = self._shots("test__01__friendly_token_upload_and_resolve",                  # todo: resolve this automatically from the current test name (which is the one that should control this value (since if we change the test name, we don't have to worry about keeping this value in sync)
                                    self.test__01__friendly_token_upload_and_resolve.__doc__)       # todo: using __doc__ here is a good idea, but this description should not be defined here (since this text should be created by an LLM that has access to the code of this test and the screenshots)
        friendly_token = self._upload_with_simple_token(shots)                                      # todo: this is good, but we shouldn't be using a helper method (_upload_with_simple_token) inside this test_Friendly_Token class (since now we have two places to maintain any changes to the upload logic. this is another good example of where we should be leveraging a Upload Brwoser automation class, which is specific to the Page)
                                                                                                    # todo: also , probably not for this case, but for tests that need a fresh friendly token, we should also have fast ways to do that: direct memory injection (to the in memory SG/Send server, direct API class to the Fast_API service. In this cases we can't use http requests to the server, since those are all static pages :) )
        assert friendly_token                       , "No friendly token found after upload"
        assert TOKEN_PATTERN.search(friendly_token) , f"Token does not match word-word-NNNN pattern: {friendly_token!r}"
        shots.capture(self.sg_send.raw_page(), "05_token_captured", f"Token: {friendly_token}")

        # Resolve in new page
        new_page = self.sg_send.raw_page().context.new_page()
        # todo: we should never do this, since it anything fails here, the test should fail since it represents something to fix
        try:
            from tests.qa.v030.browser_helpers import goto, wait_for_download_states            # todo: we should not be doing direct imports here since they add complexity to the code
            goto(new_page, f"{self.harness.ui_url()}/en-gb/browse/#{friendly_token}")           # todo: we should not use goto in tests like this, since the full logic should be captured in respective Page class
            wait_for_download_states(new_page, ["complete", "error"])                           # todo: we need a much better way to do this, ideally one based on the events raised by the code in the page (i.e. the browser)
            shots.capture(new_page, "06_token_resolved", f"Token '{friendly_token}' resolved")
            resolve_text = new_page.text_content("body") or ""
            assert "not found" not in resolve_text.lower(), f"Token resolution failed — 'not found' error. Token: {friendly_token}"
        finally:
            new_page.close()
        shots.save_metadata()

    def test__02__friendly_token_format(self):
        """Verify the friendly token matches the word-word-NNNN pattern."""
        shots          = self._shots("test__02__friendly_token_format",
                                     self.test__02__friendly_token_format.__doc__)
        friendly_token = self._upload_with_simple_token(shots, filename="format-test.txt")

        assert friendly_token, "No friendly token found after upload"
        parts = friendly_token.strip().split("-")
        assert len(parts) == 3,        f"Token should have 3 parts: {friendly_token}"
        assert parts[0].isalpha(),     f"First part should be a word: {parts[0]}"
        assert parts[1].isalpha(),     f"Second part should be a word: {parts[1]}"
        assert parts[2].isdigit(),     f"Third part should be digits: {parts[2]}"
        assert len(parts[2]) == 4,     f"Third part should be 4 digits: {parts[2]}"
        shots.save_metadata()

    def test__03__friendly_token_resolves_in_new_tab(self):
        """Upload with Simple Token, then open the token in a new browser tab."""
        shots          = self._shots("test__03__friendly_token_resolves_in_new_tab",
                                     self.test__03__friendly_token_resolves_in_new_tab.__doc__)
        friendly_token = self._upload_with_simple_token(shots, filename="resolve-test.txt")

        assert friendly_token, "No friendly token found after upload"
        new_page = self.sg_send.raw_page().context.new_page()
        try:
            from tests.qa.v030.browser_helpers import goto, wait_for_download_states
            goto(new_page, f"{self.harness.ui_url()}/en-gb/browse/#{friendly_token}")
            wait_for_download_states(new_page, ["complete", "error"])
            shots.capture(new_page, "05_token_resolved", f"Token '{friendly_token}'")
            resolve_text = new_page.text_content("body") or ""
            assert "not found" not in resolve_text.lower(), \
                f"Token resolution failed — this is the P0 bug. Token: {friendly_token}"
            assert SAMPLE_CONTENT in resolve_text or len(resolve_text) > 100, \
                "Token did not resolve to decrypted content"
        finally:
            new_page.close()
        shots.save_metadata()

    def test__04__friendly_token_no_key_in_url_after_decrypt(self):
        """After decryption, the friendly token remains in the URL (by design)."""
        shots          = self._shots("test__04__friendly_token_no_key_in_url_after_decrypt",
                                     self.test__04__friendly_token_no_key_in_url_after_decrypt.__doc__)
        friendly_token = self._upload_with_simple_token(shots, filename="url-test.txt")

        assert friendly_token, "No friendly token found"
        new_page = self.sg_send.raw_page().context.new_page()
        try:
            from tests.qa.v030.browser_helpers import goto, wait_for_download_states
            goto(new_page, f"{self.harness.ui_url()}/en-gb/browse/#{friendly_token}")
            wait_for_download_states(new_page, ["complete", "error"])
            final_url = new_page.url
            shots.capture(new_page, "05_hash_after_decrypt", f"URL after decrypt: {final_url}")
            if "#" in final_url:
                hash_fragment = final_url.split("#", 1)[1]
                assert TOKEN_PATTERN.match(hash_fragment) or hash_fragment == "", \
                    f"URL hash is neither a friendly token nor empty: {hash_fragment}"
        finally:
            new_page.close()
        shots.save_metadata()
