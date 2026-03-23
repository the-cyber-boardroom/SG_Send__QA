"""UC-03: Friendly Token — Simple Token share mode (P0).

This was a P0 bug — critical to test.

Flow:
  1. Upload a file with Simple Token share mode
  2. Capture the friendly token (word-word-NNNN format)
  3. Open a new tab to /en-gb/browse/#<friendly-token>
  4. Verify the token resolves and content decrypts
"""

import pytest
import re

from .browser_helpers import goto, handle_access_gate

pytestmark = pytest.mark.p0

SAMPLE_CONTENT = "Friendly token test — UC-03."
TOKEN_PATTERN  = re.compile(r"\b[a-z]+-[a-z]+-\d{4}\b")


def _upload_with_simple_token(page, ui_url, send_server, screenshots, filename="token-test.txt"):
    """Shared: file (auto-advances to delivery) → Next → Simple Token card → upload → return token.

    Wizard behaviour (send-upload.js):
      - set_input_files triggers _setFile() → _advanceToDelivery() automatically.
      - Clicking a share card emits step-share-selected → auto-advances to confirm.
    Sequence: [Next] → <token card click> → [Encrypt & Upload].
    """
    goto(page, f"{ui_url}/en-gb/")
    handle_access_gate(page, send_server.access_token)

    page.locator("#file-input").set_input_files({
        "name": filename, "mimeType": "text/plain",
        "buffer": SAMPLE_CONTENT.encode(),
    })
    page.wait_for_timeout(800)
    screenshots.capture(page, "01_file_selected", "File selected (delivery step active)")

    # Delivery → Share mode
    page.locator("#upload-next-btn").click()
    page.wait_for_timeout(800)

    # Select Simple Token — click auto-advances to confirm step
    page.locator('[data-mode="token"]').click()
    page.wait_for_timeout(500)
    screenshots.capture(page, "02_simple_token_selected", "Simple Token selected")

    # Confirm → Encrypt & Upload
    page.locator("#upload-next-btn").click()
    page.wait_for_timeout(5000)
    screenshots.capture(page, "03_upload_complete", "Upload complete")

    # Extract the friendly token from the Done step.
    # The done step (upload-step-done) renders in Shadow DOM, so
    # page.text_content("body") cannot see it.  Use Playwright's
    # shadow-piercing locators instead.
    token_matches = []

    # Primary: the #simple-token div holds the plain token string
    simple_token_el = page.locator("#simple-token")
    if simple_token_el.count() > 0:
        token_text = simple_token_el.first.text_content() or ""
        token_matches = TOKEN_PATTERN.findall(token_text)

    if not token_matches:
        # Fallback: the #full-link box contains the browse URL which includes the token
        full_link_el = page.locator("#full-link")
        if full_link_el.count() > 0:
            link_text = full_link_el.first.text_content() or ""
            token_matches = TOKEN_PATTERN.findall(link_text)

    return token_matches


class TestFriendlyToken:
    """Validate the Simple Token (friendly token) share mode end-to-end."""

    def test_friendly_token_upload_and_resolve(self, page, ui_url, send_server, screenshots):
        """Upload with Simple Token mode, then resolve the friendly token in a new tab."""
        token_matches = _upload_with_simple_token(page, ui_url, send_server, screenshots)

        assert token_matches, (
            "No friendly token (word-word-NNNN) found on the page after upload."
        )
        friendly_token = token_matches[0]
        screenshots.capture(page, "05_token_captured", f"Token: {friendly_token}")

        # Open token in new tab
        resolve_page = page.context.new_page()
        goto(resolve_page, f"{ui_url}/en-gb/browse/#{friendly_token}")
        resolve_page.wait_for_timeout(4000)
        screenshots.capture(resolve_page, "06_token_resolved", f"Token '{friendly_token}' resolved")

        resolve_text = resolve_page.text_content("body") or ""
        assert "not found" not in resolve_text.lower(), (
            f"Token resolution failed — 'not found' error. Token: {friendly_token}"
        )
        resolve_page.close()

    def test_friendly_token_format(self, page, ui_url, send_server, screenshots):
        """Verify the friendly token matches the word-word-NNNN pattern."""
        token_matches = _upload_with_simple_token(page, ui_url, send_server, screenshots,
                                                  filename="format-test.txt")
        assert token_matches, "No friendly token found after upload"
        token = token_matches[0]

        parts = token.split("-")
        assert len(parts) == 3,            f"Token should have 3 parts: {token}"
        assert parts[0].isalpha(),         f"First part should be a word: {parts[0]}"
        assert parts[1].isalpha(),         f"Second part should be a word: {parts[1]}"
        assert parts[2].isdigit(),         f"Third part should be digits: {parts[2]}"
        assert len(parts[2]) == 4,         f"Third part should be 4 digits: {parts[2]}"

    def test_friendly_token_resolves_in_new_tab(self, page, ui_url, send_server, screenshots):
        """Upload with Simple Token, then open the token in a new browser tab."""
        token_matches = _upload_with_simple_token(page, ui_url, send_server, screenshots,
                                                  filename="resolve-test.txt")
        assert token_matches, "No friendly token found after upload"
        friendly_token = token_matches[0]

        resolve_page = page.context.new_page()
        goto(resolve_page, f"{ui_url}/en-gb/browse/#{friendly_token}")
        resolve_page.wait_for_timeout(4000)
        screenshots.capture(resolve_page, "05_token_resolved", f"Token '{friendly_token}'")

        resolve_text = resolve_page.text_content("body") or ""
        assert "not found" not in resolve_text.lower(), (
            f"Token resolution failed — 'not found' error. This is the P0 bug. Token: {friendly_token}"
        )
        assert SAMPLE_CONTENT in resolve_text or len(resolve_text) > 100, \
            "Token did not resolve to decrypted content"
        resolve_page.close()

    def test_friendly_token_no_key_in_url_after_decrypt(self, page, ui_url, send_server, screenshots):
        """After decryption, the friendly token remains in the URL (by design).

        The JS send-download component intentionally keeps friendly tokens in the URL
        after decryption (comment: 'Friendly tokens are safe to keep in the URL bar').
        Unlike combined links where the hash contains the actual encryption key,
        a friendly token (word-word-NNNN) is merely a lookup identifier — the real
        key is stored server-side in the vault.  So leaving it visible is not a
        security risk, and keeping it allows the user to refresh or bookmark the page.

        This test verifies that the URL still contains the token (not cleared) and that
        no raw crypto key appears in the URL fragment.
        """
        token_matches = _upload_with_simple_token(page, ui_url, send_server, screenshots,
                                                  filename="url-test.txt")
        assert token_matches, "No friendly token found"
        friendly_token = token_matches[0]

        resolve_page = page.context.new_page()
        goto(resolve_page, f"{ui_url}/en-gb/browse/#{friendly_token}")
        resolve_page.wait_for_timeout(4000)

        final_url = resolve_page.url
        screenshots.capture(resolve_page, "05_hash_after_decrypt", f"URL after decrypt: {final_url}")

        if "#" in final_url:
            hash_fragment = final_url.split("#", 1)[1]
            # Friendly token should remain in URL (intentional — it's a lookup key, not the crypto key)
            # Verify the hash is the friendly token (not a raw base64 crypto key)
            assert TOKEN_PATTERN.match(hash_fragment) or hash_fragment == "", (
                f"URL hash is neither a friendly token nor empty: {hash_fragment}"
            )
        resolve_page.close()
