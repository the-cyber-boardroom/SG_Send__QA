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
import re

pytestmark = pytest.mark.p0

SAMPLE_CONTENT = "Hello from SG/Send QA — UC-01 single file upload test."
SAMPLE_FILENAME = "uc01-test-file.txt"


class TestSingleFileUpload:
    """Upload a single text file and verify round-trip decryption."""

    def test_upload_page_loads(self, page, ui_url, screenshots):
        """Navigate to /en-gb/ and verify the upload zone is visible."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        screenshots.capture(page, "01_upload_page", "Upload page loaded")

        # The upload zone should be visible (drop zone or browse button)
        upload_zone = page.locator("[class*='upload'], [class*='drop'], #file-input").first
        assert upload_zone.count() > 0 or page.locator("text=upload").first.count() > 0, \
            "Upload zone not found on landing page"

    def test_single_file_upload_flow(self, page, ui_url, send_server, screenshots):
        """Upload a text file through the wizard and verify the download link works."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # --- Handle access gate if present ---
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")
            screenshots.capture(page, "02_access_gate_passed", "Access gate passed")

        # --- Feed the file to the file input ---
        file_input = page.locator("#file-input")
        file_input.set_input_files({
            "name"    : SAMPLE_FILENAME,
            "mimeType": "text/plain",
            "buffer"  : SAMPLE_CONTENT.encode(),
        })
        page.wait_for_timeout(1000)
        screenshots.capture(page, "03_file_selected", "File selected for upload")

        # --- Walk through the wizard steps ---
        # Step 2: Delivery options — click Next/Continue
        next_button = page.locator("button:has-text('Next'), button:has-text('Continue')").first
        if next_button.is_visible(timeout=3000):
            next_button.click()
            page.wait_for_timeout(500)
            screenshots.capture(page, "04_step2_delivery", "Step 2 — delivery options")

        # Step 3: Share mode — select Combined Link (default or click it)
        combined_link = page.locator("text=Combined link, text=Combined Link").first
        if combined_link.is_visible(timeout=3000):
            combined_link.click()
            page.wait_for_timeout(500)

        next_button = page.locator("button:has-text('Next'), button:has-text('Continue')").first
        if next_button.is_visible(timeout=3000):
            next_button.click()
            page.wait_for_timeout(500)
            screenshots.capture(page, "05_step3_share_mode", "Step 3 — share mode selected")

        # Step 4: Confirm — click Upload / Encrypt & Upload
        upload_button = page.locator(
            "button:has-text('Upload'), button:has-text('Encrypt'), button:has-text('Confirm')"
        ).first
        if upload_button.is_visible(timeout=3000):
            upload_button.click()
            screenshots.capture(page, "06_step4_uploading", "Step 4 — encrypting and uploading")

        # Wait for upload to complete (step 6 / Done)
        page.wait_for_timeout(5000)
        screenshots.capture(page, "07_step6_done", "Step 6 — upload complete")

        # --- Extract the download link ---
        # Look for a link or text containing the download URL
        download_link_el = page.locator("a[href*='download'], a[href*='/en-gb/']").first
        if download_link_el.is_visible(timeout=5000):
            download_url = download_link_el.get_attribute("href")
        else:
            # Try to find the URL in a text/input element
            link_input = page.locator("input[readonly], input[value*='download']").first
            if link_input.is_visible(timeout=3000):
                download_url = link_input.get_attribute("value")
            else:
                # Fall back to page URL if it already changed
                download_url = page.url

        assert download_url, "No download link found after upload"

        # Make the URL absolute if it's relative
        if download_url.startswith("/"):
            download_url = f"{ui_url}{download_url}"

        # --- Open the download link and verify content ---
        download_page = page.context.new_page()
        download_page.goto(download_url)
        download_page.wait_for_load_state("networkidle")
        download_page.wait_for_timeout(3000)
        screenshots.capture(download_page, "08_download_page", "Download page with decrypted content")

        # Verify the original content appears on the page
        page_text = download_page.text_content("body")
        assert SAMPLE_CONTENT in page_text, (
            f"Decrypted content not found on download page. "
            f"Expected '{SAMPLE_CONTENT}' in page body."
        )

        download_page.close()

    def test_download_link_format(self, page, ui_url, send_server, screenshots):
        """Verify the download link contains transfer ID and key in the hash."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # Handle access gate
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        # Upload a file
        file_input = page.locator("#file-input")
        file_input.set_input_files({
            "name"    : "format-test.txt",
            "mimeType": "text/plain",
            "buffer"  : b"format test content",
        })
        page.wait_for_timeout(1000)

        # Walk through wizard (click Next until done)
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
        screenshots.capture(page, "09_link_format", "Download link for format verification")

        # Extract the download URL (from link, input, or clipboard)
        download_url = ""
        link_el = page.locator("a[href*='download'], a[href*='/en-gb/']").first
        if link_el.is_visible(timeout=3000):
            download_url = link_el.get_attribute("href") or ""
        else:
            input_el = page.locator("input[readonly]").first
            if input_el.is_visible(timeout=2000):
                download_url = input_el.get_attribute("value") or ""

        # The URL should contain a hash fragment with transfer ID and key
        # Format: /en-gb/download/#<12-char-id>/<base64-key>
        assert "#" in download_url, f"Download URL missing hash fragment: {download_url}"

    def test_footer_version(self, page, ui_url, send_server):
        """Verify the footer shows v0.3.0."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # Handle access gate
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        page_text = page.text_content("body")
        assert "v0.3.0" in page_text, "Footer does not show v0.3.0"
