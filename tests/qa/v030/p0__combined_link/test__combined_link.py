"""UC-04: Combined Link share mode (P0).

Flow:
  1. Upload a file with Combined Link share mode
  2. Capture the full link (contains #transferId/base64key)
  3. Open the link in a new tab
  4. Verify auto-decrypt and content display
"""

import pytest
import re

from tests.qa.v030.browser_helpers import goto, handle_access_gate

pytestmark = pytest.mark.p0

SAMPLE_CONTENT = "Combined link test — UC-04."


def _upload_and_select_mode(page, ui_url, send_server, screenshots, mode_data_attr, step2_label):
    """Shared wizard flow: file → (auto delivery) → Next → pick share mode → upload.

    Wizard behaviour (send-upload.js):
      - set_input_files triggers _setFile() → _advanceToDelivery() automatically.
        No extra Next click needed to reach the delivery step.
      - Clicking a share card emits step-share-selected → wizard auto-advances to
        confirm.  No extra Next click needed after card selection.
    So the minimal button sequence is: [Next] → <card click> → [Encrypt & Upload].
    """
    goto(page, f"{ui_url}/en-gb/")
    handle_access_gate(page, send_server.access_token)

    # Attach file — _setFile() auto-advances wizard to delivery step
    page.locator("#file-input").set_input_files({
        "name": "combined-link-test.txt", "mimeType": "text/plain",
        "buffer": SAMPLE_CONTENT.encode(),
    })
    page.wait_for_timeout(800)
    screenshots.capture(page, "01_file_selected", "File selected (delivery step active)")

    # Delivery → Share mode
    page.locator("#upload-next-btn").click()
    page.wait_for_timeout(800)
    screenshots.capture(page, "02_share_step", "Share mode step")

    # Select share mode card — click auto-advances to confirm step
    page.locator(f'[data-mode="{mode_data_attr}"]').click()
    page.wait_for_timeout(500)
    screenshots.capture(page, "03_mode_selected", f"{step2_label} selected")

    # Confirm → Encrypt & Upload
    page.locator("#upload-next-btn").click()
    page.wait_for_timeout(5000)   # wait for encrypt + upload
    screenshots.capture(page, "04_upload_complete", "Upload complete")


class TestCombinedLink:
    """Validate the Combined Link share mode end-to-end."""

    def test_combined_link_upload_and_auto_decrypt(self, page, ui_url, send_server, screenshots):
        """Upload with Combined Link, open the link, verify auto-decryption."""
        _upload_and_select_mode(page, ui_url, send_server, screenshots, "combined", "Combined link")

        # --- Extract the download link from the Done step ---
        download_url = ""
        for input_el in page.locator("input[readonly]").all():
            val = input_el.get_attribute("value") or ""
            if "#" in val:
                download_url = val
                break
        if not download_url:
            link_el = page.locator("a[href*='#']").first
            if link_el.is_visible(timeout=2000):
                download_url = link_el.get_attribute("href") or ""

        assert download_url, "No combined link found after upload"
        screenshots.capture(page, "06_link_captured", f"Combined link: {download_url[:80]}")

        # Verify format: contains #<id>/<key>
        assert "#" in download_url, f"Combined link missing hash fragment: {download_url}"
        hash_part = download_url.split("#", 1)[1]
        parts = hash_part.split("/", 1)
        assert len(parts) == 2 and len(parts[0]) >= 8 and parts[1], (
            f"Hash should be #<transferId>/<base64key>: #{hash_part}"
        )

        # Open in new tab and verify auto-decrypt
        if download_url.startswith("/"):
            download_url = f"{ui_url}{download_url}"
        dl_page = page.context.new_page()
        goto(dl_page, download_url)
        dl_page.wait_for_timeout(4000)   # allow JS decrypt
        screenshots.capture(dl_page, "07_auto_decrypted", "Auto-decrypted content")

        body_text = dl_page.text_content("body") or ""
        key_input = dl_page.locator("#decrypt-key-input, input[placeholder*='key']")
        assert not key_input.is_visible(timeout=500), \
            "Combined link should auto-decrypt — key input should not appear"
        assert SAMPLE_CONTENT in body_text, \
            f"Decrypted content not found. Page snippet: {body_text[:300]}"
        dl_page.close()

    def test_combined_link_via_api_helper(self, page, ui_url, transfer_helper, screenshots):
        """Create an encrypted transfer via API helper, then open the combined link in browser."""
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=SAMPLE_CONTENT.encode(),
            filename="api-combined-test.txt",
        )
        combined_url = f"{ui_url}/en-gb/browse/#{tid}/{key_b64}"

        goto(page, combined_url)
        page.wait_for_timeout(4000)   # allow JS decrypt
        screenshots.capture(page, "01_api_created_decrypt",
                            "Decrypted content from API-created transfer")

        body_text = page.text_content("body") or ""
        assert SAMPLE_CONTENT in body_text, \
            f"API-created transfer did not decrypt. Transfer ID: {tid}"
