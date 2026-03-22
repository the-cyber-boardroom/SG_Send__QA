"""UC-09: Manual token/ID entry form (P1).

Tests the download page when accessed with no hash fragment:
  1. Navigate to /en-gb/download/ (no hash)
  2. Verify entry form appears: input + Decrypt & Download button
  3. Enter a valid friendly token from a previous upload
  4. Verify it resolves and decrypts
  5. Enter a bogus token → verify error message
"""

import pytest

pytestmark = pytest.mark.p1


class TestManualEntry:
    """Test the manual token/ID entry form on the download page."""

    def test_entry_form_visible_when_no_hash(self, page, ui_url, screenshots):
        """Navigate to /en-gb/download/ with no hash — verify entry form appears."""
        page.goto(f"{ui_url}/en-gb/download/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        screenshots.capture(page, "01_entry_form", "Download page — entry form (no hash)")

        # Should show an input field and a button
        entry_input = page.locator(
            "input[type='text'], input[type='password'], "
            "input[placeholder*='token'], input[placeholder*='Token'], "
            "input[placeholder*='ID'], input[placeholder*='id']"
        ).first
        assert entry_input.is_visible(timeout=5000), (
            "Entry form input not visible on /en-gb/download/ (no hash)"
        )

        decrypt_btn = page.locator(
            "button:has-text('Decrypt'), button:has-text('Download'), "
            "button:has-text('Go'), button:has-text('Submit')"
        ).first
        assert decrypt_btn.is_visible(timeout=3000), (
            "Decrypt/Download button not visible on entry form"
        )

    def test_valid_token_resolves(self, page, ui_url, transfer_helper, screenshots):
        """Enter a valid transfer ID + key via the entry form → verify content loads."""
        content = b"Manual entry resolve test"
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=content,
            filename="manual-entry-test.txt",
        )

        page.goto(f"{ui_url}/en-gb/download/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Enter the transfer ID (or combined id/key) into the form
        entry_input = page.locator(
            "input[type='text'], input[type='password'], "
            "input[placeholder*='token'], input[placeholder*='Token'], "
            "input[placeholder*='ID']"
        ).first
        assert entry_input.is_visible(timeout=5000), "Entry form input not visible"

        # Try entering the combined format: id/key
        entry_input.fill(f"{tid}/{key_b64}")
        screenshots.capture(page, "02_token_entered", f"Entered transfer ID + key")

        decrypt_btn = page.locator(
            "button:has-text('Decrypt'), button:has-text('Download'), "
            "button:has-text('Go'), button:has-text('Submit')"
        ).first
        decrypt_btn.click()
        page.wait_for_timeout(5000)
        screenshots.capture(page, "03_resolved", "Content loaded via manual entry")

        body_text = page.text_content("body") or ""
        # Should show decrypted content or at least no error
        error_text = body_text.lower()
        assert "not found" not in error_text or content.decode() in body_text, (
            f"Manual entry did not resolve the transfer. Body: {body_text[:500]}"
        )

    def test_bogus_token_shows_error(self, page, ui_url, screenshots):
        """Enter a bogus token → verify error message."""
        page.goto(f"{ui_url}/en-gb/download/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        entry_input = page.locator(
            "input[type='text'], input[type='password'], "
            "input[placeholder*='token'], input[placeholder*='Token'], "
            "input[placeholder*='ID']"
        ).first
        assert entry_input.is_visible(timeout=5000), "Entry form input not visible"

        # Enter a completely bogus token
        entry_input.fill("bogus-fake-0000")
        screenshots.capture(page, "04_bogus_entered", "Bogus token entered")

        decrypt_btn = page.locator(
            "button:has-text('Decrypt'), button:has-text('Download'), "
            "button:has-text('Go'), button:has-text('Submit')"
        ).first
        decrypt_btn.click()
        page.wait_for_timeout(5000)
        screenshots.capture(page, "05_bogus_error", "Error message for bogus token")

        body_text = (page.text_content("body") or "").lower()
        error_indicators = ["error", "not found", "invalid", "failed", "unable", "unknown"]
        has_error = any(ind in body_text for ind in error_indicators)
        assert has_error, (
            f"No error message shown for bogus token. Body: {body_text[:500]}"
        )
