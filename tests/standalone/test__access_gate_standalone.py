"""Standalone test: Access Token Gate (UC-10).

Self-contained browser test for the access gate use case.
Independent of the v030 test suite (which is under active refactoring).

Run with:
    source /tmp/venv312/bin/activate
    python -m pytest tests/standalone/test__access_gate_standalone.py -v --tb=short

Screenshots are saved to:
    sg_send_qa__site/pages/use-cases/access_gate/screenshots/

These screenshots are auto-committed by CI and deployed to:
    https://qa.send.sgraph.ai/pages/use-cases/access_gate/
"""

import pytest


class TestAccessGate:
    """Verify the access token gate on the upload page."""

    def test_upload_accessible_with_token(self, page, ui_url, send_server, screenshots):
        """Providing the correct access token grants access to the upload zone."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        screenshots.capture(page, "01_landing", "Landing page (may show gate or upload zone)")

        # Check if access gate is present
        gate_input = page.locator("#access-token-input")
        if gate_input.is_visible(timeout=3000):
            gate_input.fill(send_server.access_token)
            page.locator("#access-token-submit").click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            screenshots.capture(page, "02_after_token", "After entering access token")

        # Upload zone should now be visible
        file_input  = page.locator("input[type='file']")
        page_text   = page.text_content("body") or ""
        has_upload  = file_input.count() > 0
        has_keyword = any(kw in page_text.lower() for kw in ["upload", "drop", "browse", "choose"])

        assert has_upload or has_keyword, \
            "Upload zone not visible after providing valid access token"

    def test_wrong_token_shows_error(self, page, ui_url, send_server, screenshots):
        """Providing a wrong access token shows an error."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        gate_input = page.locator("#access-token-input")
        if gate_input.is_visible(timeout=3000):
            gate_input.fill("wrong-token-12345-xxxxx")
            page.locator("#access-token-submit").click()
            page.wait_for_timeout(1000)
            screenshots.capture(page, "03_wrong_token", "Wrong token response")

            page_text = page.text_content("body") or ""
            assert any(kw in page_text.lower() for kw in [
                "error", "invalid", "wrong", "incorrect", "denied"
            ]) or gate_input.is_visible(), \
                "No error shown for wrong access token"

    def test_upload_zone_visible_without_gate(self, page, ui_url, send_server, screenshots):
        """If no gate is configured, upload zone is immediately visible."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        gate_input = page.locator("#access-token-input")
        if gate_input.is_visible(timeout=2000):
            pytest.skip("Access gate is active; testing gated flow in other tests")

        file_input = page.locator("input[type='file']")
        screenshots.capture(page, "04_no_gate", "Upload zone without gate")
        page_text = page.text_content("body") or ""
        assert file_input.count() > 0 or any(kw in page_text.lower() for kw in [
            "upload", "drop", "browse"
        ]), "Upload zone not visible (and no gate present)"


class TestAccessGateHealthCheck:
    """API health check — no browser needed."""

    def test_health_endpoint(self, send_server):
        """Health endpoint returns 200."""
        import httpx
        r = httpx.get(f"{send_server.server_url}/info/health")
        assert r.status_code == 200, f"Health check failed: {r.status_code}"
