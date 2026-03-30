"""UC-10: Access token gate — browser tests (P1).

Test flow:
  - Navigate to /en-gb/ (upload page)
  - If access gate is active, verify token entry UI appears
  - Enter the valid access token → verify upload zone becomes visible
  - Verify wrong token shows an error

API-level tests (token counter) live in via__httpx/test__access_gate.py.

v0.3.1 notes:
  - CR-001: Use body[data-ready] instead of networkidle.
  - CR-002: Use data-testid selectors for access gate elements:
      [data-testid="access-gate-input"]   (was #access-token-input)
      [data-testid="access-gate-submit"]  (was #access-token-submit)
      [data-testid="access-gate-error"]   (was generic text search)
    ID selectors (#access-token-input) are preserved for backward compatibility
    and still work, but data-testid is the preferred stable selector.
"""

import pytest

pytestmark = pytest.mark.p1


class TestAccessGate:
    """Verify the access token gate on the upload page."""

    def _load_upload_page(self, page, ui_url):
        """Navigate to the upload page and wait for it to be ready."""
        page.goto(f"{ui_url}/en-gb/", wait_until="commit")
        page.wait_for_selector("body[data-ready]", timeout=10_000)

    def test_upload_accessible_with_token(self, page, ui_url, send_server, screenshots):
        """Providing the correct access token grants access to the upload zone."""
        self._load_upload_page(page, ui_url)
        screenshots.capture(page, "01_landing", "Landing page (may show gate or upload zone)")

        # CR-002: prefer data-testid; fall back to ID for older UI versions
        gate_input = page.locator('[data-testid="access-gate-input"], #access-token-input').first
        if gate_input.is_visible(timeout=3_000):
            gate_input.fill(send_server.access_token)
            page.locator('[data-testid="access-gate-submit"], #access-token-submit').first.click()
            page.wait_for_selector("body[data-ready]", timeout=10_000)
            page.wait_for_timeout(800)

            # Verify no unexpected UI is overlaying the page (e.g. language dropdown)
            page_text = page.text_content("body") or ""
            unexpected_dropdown = any(lang in page_text for lang in [
                "Deutsch", "Italiano", "Polski",
            ])
            assert not unexpected_dropdown, \
                "Language dropdown is open — see bugs/test__bug__generic_button_opens_language_dropdown.py"

            screenshots.capture(page, "02_after_token", "After entering access token")

        # Upload zone should now be visible
        file_input  = page.locator("#file-input, [data-testid='file-input']").first
        page_text   = page.text_content("body") or ""
        has_upload  = file_input.count() > 0
        has_keyword = any(kw in page_text.lower() for kw in [
            "upload", "drop", "browse", "choose"
        ])

        assert has_upload or has_keyword, \
            "Upload zone not visible after providing valid access token"

    def test_wrong_token_shows_error(self, page, ui_url, send_server, screenshots):
        """Providing a wrong access token shows an error."""
        self._load_upload_page(page, ui_url)

        gate_input = page.locator('[data-testid="access-gate-input"], #access-token-input').first
        if gate_input.is_visible(timeout=3_000):
            gate_input.fill("wrong-token-12345-xxxxx")
            page.locator('[data-testid="access-gate-submit"], #access-token-submit').first.click()
            page.wait_for_timeout(1_000)
            screenshots.capture(page, "03_wrong_token", "Wrong token response")

            # CR-002: data-testid="access-gate-error" is the error element
            error_el = page.locator('[data-testid="access-gate-error"]').first
            if error_el.is_visible(timeout=2_000):
                error_text = error_el.text_content() or ""
                assert error_text.strip(), "access-gate-error element is visible but empty"
            else:
                # Fallback: check body text or that gate is still visible
                page_text = page.text_content("body") or ""
                assert any(kw in page_text.lower() for kw in [
                    "error", "invalid", "wrong", "incorrect", "denied"
                ]) or gate_input.is_visible(), \
                    "No error shown for wrong access token"

    def test_upload_zone_visible_without_gate(self, page, ui_url, send_server, screenshots):
        """If no gate is configured, upload zone is immediately visible."""
        self._load_upload_page(page, ui_url)

        gate_input = page.locator('[data-testid="access-gate-input"], #access-token-input').first
        if gate_input.is_visible(timeout=2_000):
            pytest.skip("Access gate is active; testing gated flow in other tests")

        # No gate — upload zone should be directly visible
        file_input = page.locator("#file-input, [data-testid='file-input']").first
        screenshots.capture(page, "04_no_gate", "Upload zone without gate")
        page_text = page.text_content("body") or ""
        assert file_input.count() > 0 or any(kw in page_text.lower() for kw in [
            "upload", "drop", "browse"
        ]), "Upload zone not visible (and no gate present)"
