"""UC-01: Single file upload → download → content matches (P0).

Happy-path end-to-end test:
  1. Navigate to the upload page
  2. Drop a text file onto the upload zone
  3. Walk through the 6-step wizard
  4. Capture the download link
  5. Open the download link in a new page
  6. Verify decrypted content matches the original
"""

import pytest

from playwright.sync_api import expect
from tests.qa.v030.browser_helpers import goto, handle_access_gate

pytestmark = pytest.mark.p0

SAMPLE_CONTENT  = "Hello from SG/Send QA — UC-01 single file upload test."
SAMPLE_FILENAME = "uc01-test-file.txt"


def _upload_file(page, ui_url, send_server, screenshots, filename, content_bytes):
    """Navigate to upload page, handle gate, select file, walk wizard, return download URL.

    Wizard behaviour (send-upload.js):
      - set_input_files triggers _setFile() → _advanceToDelivery() automatically.
        A brief pause (800ms) lets the wizard register the file before we click Next.
      - Clicking a share card emits step-share-selected → wizard auto-advances to
        confirm.  A brief pause (500ms) lets the transition settle before clicking Next.
    Minimal button sequence: <pause> → [Next] → <card click> → <pause> → [Encrypt & Upload]
    """
    goto(page, f"{ui_url}/en-gb/")
    handle_access_gate(page, send_server.access_token)

    page.locator("#file-input").set_input_files({
        "name"    : filename,
        "mimeType": "text/plain",
        "buffer"  : content_bytes,
    })
    # Brief pause for wizard to register file and auto-advance to delivery step
    page.wait_for_timeout(800)
    screenshots.capture(page, "01_file_selected", "File selected — delivery step")

    # Delivery → Share mode
    page.locator("#upload-next-btn").click()
    page.locator("[data-mode]").first.wait_for(state="visible")
    screenshots.capture(page, "02_share_step", "Share mode step")

    # Select combined link — auto-advances to confirm step
    page.locator('[data-mode="combined"]').click()
    page.wait_for_timeout(500)  # let confirm step transition settle
    screenshots.capture(page, "03_mode_selected", "Combined link selected")

    # Confirm → Encrypt & Upload — done step shows the link as <a href>
    page.locator("#upload-next-btn").click()
    # Wait for the download link to appear in the done step
    page.locator("a[href*='#']").first.wait_for(state="attached", timeout=20_000)
    screenshots.capture(page, "04_upload_done", "Upload complete — link shown")

    # Extract download URL — done step renders link as <a>, not input[readonly]
    download_url = page.locator("a[href*='#']").first.get_attribute("href") or ""
    if not download_url:
        for el in page.locator("input[readonly]").all():
            val = el.get_attribute("value") or ""
            if "#" in val:
                download_url = val
                break

    if download_url.startswith("/"):
        download_url = f"{ui_url}{download_url}"

    return download_url


class TestSingleFileUpload:
    """Upload a single text file and verify round-trip decryption."""

    def test_upload_page_loads(self, page, ui_url, screenshots):
        """Navigate to /en-gb/ and verify the upload zone is visible."""
        goto(page, f"{ui_url}/en-gb/")
        screenshots.capture(page, "01_upload_page", "Upload page loaded")

        upload_zone = page.locator("[class*='upload'], [class*='drop'], #file-input").first
        assert upload_zone.count() > 0 or page.locator("text=upload").first.count() > 0, \
            "Upload zone not found on landing page"

    def test_single_file_upload_flow(self, page, ui_url, send_server, screenshots):
        """Upload a text file through the wizard and verify the download link works."""
        download_url = _upload_file(
            page, ui_url, send_server, screenshots,
            SAMPLE_FILENAME, SAMPLE_CONTENT.encode(),
        )
        assert download_url, "No download link found after upload"
        assert "#" in download_url, f"Download URL missing hash fragment: {download_url}"

        dl_page = page.context.new_page()
        try:
            goto(dl_page, download_url)
            screenshots.capture(dl_page, "05_download_page", "Download page — awaiting decrypt")

            # Wait for decrypted content rather than an arbitrary sleep
            expect(dl_page.locator("body")).to_contain_text(SAMPLE_CONTENT, timeout=15_000)
            screenshots.capture(dl_page, "06_decrypted", "Content decrypted and visible")
        finally:
            dl_page.close()

    def test_download_link_format(self, page, ui_url, send_server, screenshots):
        """Verify the download link contains transfer ID and key in the hash."""
        download_url = _upload_file(
            page, ui_url, send_server, screenshots,
            "format-test.txt", b"format test content",
        )
        assert download_url, "No download link found after upload"
        assert "#" in download_url, f"Download URL missing hash fragment: {download_url}"

        hash_part = download_url.split("#", 1)[1]
        parts = hash_part.split("/", 1)
        assert len(parts) == 2 and len(parts[0]) >= 8 and parts[1], (
            f"Hash should be #<transferId>/<base64key>, got: #{hash_part}"
        )
        screenshots.capture(page, "07_link_format", f"Link verified: {download_url[:80]}")

    def test_footer_version(self, page, ui_url, send_server, screenshots):
        """Verify the footer shows v0.3.0."""
        goto(page, f"{ui_url}/en-gb/")
        handle_access_gate(page, send_server.access_token)

        page_text = page.text_content("body")
        assert "v0.3.0" in page_text, "Footer does not show v0.3.0"
        screenshots.capture(page, "01_footer", "Footer showing version")
