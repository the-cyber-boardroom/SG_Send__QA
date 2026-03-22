"""UC-04: Combined Link share mode (P0).

Flow:
  1. Upload a file with Combined Link share mode
  2. Capture the full link (contains #transferId/base64key)
  3. Open the link in a new tab
  4. Verify auto-decrypt and content display
"""

import pytest
import re

pytestmark = pytest.mark.p0

SAMPLE_CONTENT = "Combined link test — UC-04."


class TestCombinedLink:
    """Validate the Combined Link share mode end-to-end."""

    def test_combined_link_upload_and_auto_decrypt(self, page, ui_url, send_server, screenshots):
        """Upload with Combined Link, open the link, verify auto-decryption."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # --- Handle access gate ---
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        # --- Upload a file ---
        file_input = page.locator("input[type='file']")
        file_input.set_input_files({
            "name"    : "combined-link-test.txt",
            "mimeType": "text/plain",
            "buffer"  : SAMPLE_CONTENT.encode(),
        })
        page.wait_for_timeout(1000)
        screenshots.capture(page, "01_file_selected", "File selected for combined link test")

        # --- Navigate to share mode step and select Combined Link ---
        for _ in range(3):
            btn = page.locator("button:has-text('Next'), button:has-text('Continue')").first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)

        combined = page.locator("text=Combined link, text=Combined Link").first
        if combined.is_visible(timeout=3000):
            combined.click()
            page.wait_for_timeout(500)
        screenshots.capture(page, "02_combined_link_selected", "Combined Link share mode selected")

        # Continue through remaining steps
        for _ in range(5):
            btn = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), "
                "button:has-text('Upload'), button:has-text('Encrypt'), "
                "button:has-text('Confirm')"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(1000)

        page.wait_for_timeout(3000)
        screenshots.capture(page, "03_upload_complete", "Upload complete — combined link shown")

        # --- Extract the download link ---
        download_url = ""

        # Check link elements
        link_el = page.locator("a[href*='download'], a[href*='/en-gb/']").first
        if link_el.is_visible(timeout=3000):
            download_url = link_el.get_attribute("href") or ""

        # Check input fields
        if not download_url:
            for input_el in page.locator("input[readonly], input[value*='download']").all():
                val = input_el.get_attribute("value") or ""
                if "#" in val:
                    download_url = val
                    break

        assert download_url, "No combined link found after upload"
        screenshots.capture(page, "04_link_captured", f"Combined link: {download_url[:80]}...")

        # --- Verify URL format: /en-gb/download/#<id>/<base64key> ---
        assert "#" in download_url, f"Combined link missing hash fragment: {download_url}"
        hash_part = download_url.split("#", 1)[1]
        assert "/" in hash_part, (
            f"Hash should contain transferId/key separated by '/': #{hash_part}"
        )

        parts = hash_part.split("/", 1)
        transfer_id = parts[0]
        b64_key     = parts[1] if len(parts) > 1 else ""

        assert len(transfer_id) >= 8, f"Transfer ID too short: {transfer_id}"
        assert len(b64_key) > 0, "Base64 key is empty in combined link"

        # --- Open the link in a new tab and verify auto-decrypt ---
        if download_url.startswith("/"):
            download_url = f"{ui_url}{download_url}"

        dl_page = page.context.new_page()
        dl_page.goto(download_url)
        dl_page.wait_for_load_state("networkidle")
        dl_page.wait_for_timeout(5000)
        screenshots.capture(dl_page, "05_auto_decrypted", "Auto-decrypted content from combined link")

        # Verify auto-decryption (page should show content, not a key input)
        body_text = dl_page.text_content("body") or ""

        # Should NOT show a key entry prompt (auto-decrypt means no user action needed)
        key_input = dl_page.locator("input[type='password'], input[placeholder*='key']").first
        has_key_input = key_input.is_visible(timeout=1000) if key_input.count() > 0 else False
        assert not has_key_input, "Combined link should auto-decrypt — key input should not be shown"

        # Content should match original
        assert SAMPLE_CONTENT in body_text, (
            f"Decrypted content does not match. "
            f"Expected '{SAMPLE_CONTENT}' in page body."
        )

        dl_page.close()

    def test_combined_link_via_api_helper(self, page, ui_url, transfer_helper, screenshots):
        """Create an encrypted transfer via API, then open the combined link in browser."""
        # Use TransferHelper to create a transfer without the browser
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=SAMPLE_CONTENT.encode(),
            filename="api-combined-test.txt",
        )

        # Construct the combined link
        combined_url = f"{ui_url}/en-gb/download/#{tid}/{key_b64}"

        # Open in browser
        page.goto(combined_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "06_api_created_decrypt",
                            "Decrypted content from API-created transfer")

        body_text = page.text_content("body") or ""
        assert SAMPLE_CONTENT in body_text, (
            f"API-created transfer did not decrypt correctly. "
            f"Transfer ID: {tid}"
        )
