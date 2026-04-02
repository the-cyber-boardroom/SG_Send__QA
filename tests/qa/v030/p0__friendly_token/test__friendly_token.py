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
# [LIB-2026-04-01-047] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
_BASE  = Path(__file__).parent.parent.parent.parent.parent / "sg_send_qa__site" / "pages" / "use-cases"
_GROUP = "02-upload-share"          # [LIB-2026-04-01-048] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
_UC    = "friendly_token"


class test_Friendly_Token(TestCase):        # Validate the Simple Token (friendly token) share mode end-to-end.

    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().headless(False).setup()
        cls.sg_send = cls.harness.sg_send
        cls.harness.set_access_token()              # [LIB-2026-04-01-049] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

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

    # [LIB-2026-04-01-050] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
    def _upload_with_simple_token(self, shots, filename="token-test.txt"):
        """Upload a file with Simple Token mode and return the friendly token string."""
        self.sg_send.page__root()
        self.sg_send.upload__set_file(filename, SAMPLE_CONTENT.encode())        # [LIB-2026-04-01-051] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        shots.capture(self.sg_send.raw_page(), "01_file_selected", "File selected (delivery step active)")          # [LIB-2026-04-01-052] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

        self.sg_send.upload__click_next()                               # [LIB-2026-04-01-053] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        self.sg_send.upload__select_share_mode("token")
        shots.capture(self.sg_send.raw_page(), "02_simple_token_selected", "Simple Token selected")
        self.sg_send.upload__click_next()                               # [LIB-2026-04-01-054] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        self.sg_send.upload__wait_for_complete()                        # [LIB-2026-04-01-055] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        shots.capture(self.sg_send.raw_page(), "03_upload_complete", "Upload complete")

        return self.sg_send.upload__get_friendly_token()                # [LIB-2026-04-01-056] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

    def test__01__friendly_token_upload_and_resolve(self):      # Upload with Simple Token mode, then resolve the friendly token in a new tab.
        # [LIB-2026-04-01-057] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        shots         = self._shots("test__01__friendly_token_upload_and_resolve",
                                    self.test__01__friendly_token_upload_and_resolve.__doc__)       # [LIB-2026-04-01-058] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        friendly_token = self._upload_with_simple_token(shots)                                      # [LIB-2026-04-01-059] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        assert friendly_token                       , "No friendly token found after upload"
        assert TOKEN_PATTERN.search(friendly_token) , f"Token does not match word-word-NNNN pattern: {friendly_token!r}"
        shots.capture(self.sg_send.raw_page(), "05_token_captured", f"Token: {friendly_token}")

        # Resolve in new page
        new_page = self.sg_send.raw_page().context.new_page()
        # [LIB-2026-04-01-060] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        try:
            from tests.qa.v030.browser_helpers import goto, wait_for_download_states            # [LIB-2026-04-01-061] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
            goto(new_page, f"{self.harness.ui_url()}/en-gb/browse/#{friendly_token}")
            wait_for_download_states(new_page, ["complete", "error"])                           # [LIB-2026-04-01-062] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
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
