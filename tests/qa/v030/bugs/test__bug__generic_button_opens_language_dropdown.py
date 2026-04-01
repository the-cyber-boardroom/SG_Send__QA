"""BUG: Generic button selector opens language dropdown instead of Go.

Related: CR-002 (change-requests page)
Affects: Access gate tests (UC-10)

Root cause: The SG/Send UI renders multiple <button> elements before the
access gate's Go button:
  - Language selector button (top nav)
  - #toggle-token-vis (eye icon in the gate)
  - #access-token-submit (the actual Go button)

Using page.locator("button").first hits the language dropdown, which opens
over the page and pollutes screenshots.

This test PASSES while the bug exists (the language dropdown opens).
When the UI team fixes button ordering or adds data-testid attributes,
this test will FAIL — signalling the bug is fixed and this file can be removed.
"""

import json
import base64
from pathlib import Path

import pytest

SCREENSHOTS_DIR = Path("sg_send_qa__site/pages/use-cases/bugs/screenshots")


def _cdp_screenshot(page, path):
    """Take screenshot via CDP."""
    cdp    = page.context.new_cdp_session(page)
    result = cdp.send("Page.captureScreenshot", {"format": "png"})
    cdp.detach()
    Path(path).write_bytes(base64.b64decode(result["data"]))


class TestBug__GenericButtonOpensLanguageDropdown:
    """Reproduce: clicking first button on page opens language dropdown."""

    def test_first_button_is_not_go_button(self, page, ui_url, send_server):
        """The first <button> on the page is the language selector, not Go."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1000)

        gate_input = page.locator("#access-token-input")
        if not gate_input.is_visible(timeout=3000):
            pytest.skip("Access gate not active — cannot reproduce button ordering bug")

        # Fill token but click the FIRST button (the generic selector)
        gate_input.fill(send_server.access_token)
        first_button = page.locator("button").first

        # The bug: first button is NOT the Go button
        go_button = page.locator("#access-token-submit")
        first_button_box = first_button.bounding_box()
        go_button_box    = go_button.bounding_box()

        # They should be different elements (this assertion passes while the bug exists)
        assert first_button_box != go_button_box, \
            "BUG FIXED: first button IS now the Go button — remove this bug test"

        # Click the generic selector to show what happens
        first_button.click()
        page.wait_for_timeout(500)

        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        _cdp_screenshot(page, str(SCREENSHOTS_DIR / "bug__language_dropdown_opened.png"))

        # Verify the language dropdown opened (the bug)
        page_text = page.text_content("body") or ""
        dropdown_opened = any(lang in page_text for lang in [
            "Deutsch", "Italiano", "Polski",
        ])

        assert dropdown_opened, \
            "BUG FIXED: generic button no longer opens language dropdown — remove this bug test"
