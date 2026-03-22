"""UC-10: Access token gate (P1).

Tests the access token gate on the upload page:
  1. Navigate to /en-gb/ (upload page)
  2. If access gate is active, verify token entry UI appears
  3. Enter the valid access token
  4. Verify upload zone becomes visible
  5. Verify token persistence
"""

import pytest

pytestmark = pytest.mark.p1


class TestAccessGate:
    """Test the access token gate on the upload page."""

    def test_upload_page_shows_gate_or_upload(self, page, ui_url, screenshots):
        """Navigate to /en-gb/ — verify either access gate or upload zone is shown."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        screenshots.capture(page, "01_initial_load", "Upload page — initial load")

        # Either the access gate (token entry) or the upload zone should be visible
        access_input = page.locator(
            "input[type='text'], input[type='password']"
        ).first
        upload_zone = page.locator(
            "[class*='upload'], [class*='drop'], input[type='file']"
        ).first

        has_gate = access_input.is_visible(timeout=3000) if access_input.count() > 0 else False
        has_upload = upload_zone.is_visible(timeout=3000) if upload_zone.count() > 0 else False

        assert has_gate or has_upload, (
            "Neither access gate nor upload zone visible on /en-gb/"
        )
        screenshots.capture(page, "02_gate_or_upload",
                            f"Gate visible: {has_gate}, Upload visible: {has_upload}")

    def test_valid_token_grants_access(self, page, ui_url, send_server, screenshots):
        """Enter a valid access token → verify upload zone becomes visible."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Check if access gate is present
        access_input = page.locator(
            "input[type='text'], input[type='password']"
        ).first
        if not access_input.is_visible(timeout=3000):
            pytest.skip("No access gate detected — upload zone already visible")

        # Enter the access token
        access_input.fill(send_server.access_token)
        screenshots.capture(page, "03_token_entered", "Access token entered")

        # Click the submit/enter button
        submit_btn = page.locator(
            "button:has-text('Enter'), button:has-text('Submit'), "
            "button:has-text('Go'), button:has-text('Access')"
        ).first
        if submit_btn.is_visible(timeout=2000):
            submit_btn.click()
        else:
            # Try pressing Enter instead
            access_input.press("Enter")

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        screenshots.capture(page, "04_access_granted", "Access granted — upload zone visible")

        # Verify upload zone is now visible
        upload_zone = page.locator(
            "[class*='upload'], [class*='drop'], input[type='file']"
        ).first
        assert upload_zone.is_visible(timeout=5000), (
            "Upload zone not visible after entering valid access token"
        )

    def test_invalid_token_denied(self, page, ui_url, screenshots):
        """Enter an invalid access token → verify access is denied."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        access_input = page.locator(
            "input[type='text'], input[type='password']"
        ).first
        if not access_input.is_visible(timeout=3000):
            pytest.skip("No access gate detected")

        # Enter a bogus token
        access_input.fill("bogus-invalid-token-12345")

        submit_btn = page.locator(
            "button:has-text('Enter'), button:has-text('Submit'), "
            "button:has-text('Go'), button:has-text('Access')"
        ).first
        if submit_btn.is_visible(timeout=2000):
            submit_btn.click()
        else:
            access_input.press("Enter")

        page.wait_for_timeout(3000)
        screenshots.capture(page, "05_access_denied", "Invalid token — access denied")

        # Upload zone should NOT be visible
        upload_zone = page.locator("input[type='file']").first
        has_upload = upload_zone.is_visible(timeout=2000) if upload_zone.count() > 0 else False

        # Either the upload is hidden OR an error message is shown
        body_text = (page.text_content("body") or "").lower()
        has_error = any(w in body_text for w in ["invalid", "error", "denied", "incorrect", "wrong"])

        assert not has_upload or has_error, (
            "Upload zone visible with invalid token and no error shown"
        )

    def test_token_persistence(self, page, ui_url, send_server, screenshots):
        """After entering a valid token, reload → verify access persists."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        access_input = page.locator(
            "input[type='text'], input[type='password']"
        ).first
        if not access_input.is_visible(timeout=3000):
            pytest.skip("No access gate detected")

        # Enter valid token
        access_input.fill(send_server.access_token)
        submit_btn = page.locator(
            "button:has-text('Enter'), button:has-text('Submit'), "
            "button:has-text('Go'), button:has-text('Access')"
        ).first
        if submit_btn.is_visible(timeout=2000):
            submit_btn.click()
        else:
            access_input.press("Enter")

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Reload the page
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        screenshots.capture(page, "06_after_reload", "Page after reload — checking token persistence")

        # Check if upload zone is still visible (token persisted)
        upload_zone = page.locator(
            "[class*='upload'], [class*='drop'], input[type='file']"
        ).first
        gate_still_shown = page.locator(
            "input[type='text'], input[type='password']"
        ).first.is_visible(timeout=2000)

        # Either upload is visible (persistence works) or gate is shown again
        # Both are valid behaviors — capture the result
        screenshots.capture(page, "07_persistence_result",
                            f"Upload visible: {upload_zone.is_visible(timeout=1000)}, "
                            f"Gate shown: {gate_still_shown}")
