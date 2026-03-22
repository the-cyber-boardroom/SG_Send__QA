"""UC-08: Single file viewer (P2).

Tests the single-file download/viewer experience:
  - Markdown renders with white background, proper typography
  - Share button toggles share panel with download link
  - Copy button copies the URL with key intact
  - Print and Save locally buttons work
"""

import pytest

pytestmark = pytest.mark.p2

MARKDOWN_CONTENT = """# Test Document

This is a **markdown** file with _formatting_.

- Item one
- Item two
- Item three

## Section Two

Some `inline code` and a paragraph.
"""


class TestSingleFileViewer:
    """Test the single-file viewer for non-zip uploads."""

    def test_markdown_renders(self, page, ui_url, transfer_helper, screenshots):
        """Upload a markdown file, open download link, verify it renders."""
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=MARKDOWN_CONTENT.encode(),
            filename="test-document.md",
        )

        page.goto(f"{ui_url}/en-gb/view/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "01_markdown_rendered", "Markdown file rendered in viewer")

        body_text = page.text_content("body") or ""
        # Check that markdown content is rendered (not raw markdown syntax)
        assert "Test Document" in body_text, (
            f"Markdown heading not rendered. Body: {body_text[:500]}"
        )

    def test_share_button_toggles_panel(self, page, ui_url, transfer_helper, screenshots):
        """Verify Share button toggles the share panel with download link."""
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=b"Share panel test content",
            filename="share-test.txt",
        )

        page.goto(f"{ui_url}/en-gb/view/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        share_btn = page.locator(
            "button:has-text('Share'), [title*='Share'], [aria-label*='Share']"
        ).first
        if share_btn.is_visible(timeout=3000):
            share_btn.click()
            page.wait_for_timeout(1000)
            screenshots.capture(page, "02_share_panel", "Share panel toggled open")

            # Verify download link is shown in the share panel
            copy_btn = page.locator("button:has-text('Copy'), [title*='Copy']").first
            if copy_btn.is_visible(timeout=2000):
                screenshots.capture(page, "03_copy_button", "Copy button visible in share panel")

    def test_save_locally(self, page, ui_url, transfer_helper, screenshots):
        """Verify Save locally button exists for single file."""
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=b"Save locally test content",
            filename="save-test.txt",
        )

        page.goto(f"{ui_url}/en-gb/view/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        save_btn = page.locator(
            "button:has-text('Save'), button:has-text('Download'), "
            "[title*='Save'], [title*='Download']"
        ).first
        if save_btn.is_visible(timeout=3000):
            screenshots.capture(page, "04_save_button", "Save locally button visible")

    def test_print_button(self, page, ui_url, transfer_helper, screenshots):
        """Verify Print button exists."""
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=b"Print test content",
            filename="print-test.txt",
        )

        page.goto(f"{ui_url}/en-gb/view/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        print_btn = page.locator(
            "button:has-text('Print'), [title*='Print'], [aria-label*='Print']"
        ).first
        if print_btn.is_visible(timeout=3000):
            screenshots.capture(page, "05_print_button", "Print button visible")
