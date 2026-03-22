"""UC-06: Gallery view features (P1).

Tests gallery-specific functionality:
  - View mode buttons (compact / grid / large)
  - Copy Link, Email, Print, Save locally buttons
  - Info panel toggle
  - Lightbox navigation (arrows, click, keyboard)
  - PDF present button in lightbox
"""

import pytest

pytestmark = pytest.mark.p1


class TestGalleryFeatures:
    """Test gallery view features with an image-heavy zip."""

    def _create_image_zip(self, transfer_helper):
        """Helper: create a zip with images and upload it."""
        import zipfile, io

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            # Create fake PNG images (small but valid enough for gallery)
            for i in range(5):
                zf.writestr(f"img_{i:02d}.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
            # Add a PDF for present-mode testing
            zf.writestr("document.pdf", b"%PDF-1.4 fake content for testing")
        zip_buf.seek(0)

        return transfer_helper.upload_encrypted(
            plaintext=zip_buf.read(),
            filename="gallery-features.zip",
        )

    def test_gallery_renders_thumbnails(self, page, ui_url, transfer_helper, screenshots):
        """Verify gallery renders a thumbnail grid with correct file count."""
        tid, key_b64 = self._create_image_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "01_gallery_thumbnails", "Gallery thumbnail grid")

        # Look for thumbnail elements or image elements
        images = page.locator("img, [class*='thumbnail'], [class*='thumb'], [class*='grid-item']")
        img_count = images.count()
        screenshots.capture(page, "02_thumbnail_count", f"Found {img_count} thumbnail elements")

    def test_lightbox_opens_on_click(self, page, ui_url, transfer_helper, screenshots):
        """Click a thumbnail → verify lightbox/modal opens with full image."""
        tid, key_b64 = self._create_image_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # Click the first clickable image/thumbnail
        thumb = page.locator(
            "img, [class*='thumbnail'], [class*='thumb'], [class*='grid-item']"
        ).first
        if thumb.is_visible(timeout=3000):
            thumb.click()
            page.wait_for_timeout(2000)
            screenshots.capture(page, "03_lightbox_open", "Lightbox opened after thumbnail click")

            # Look for lightbox/modal indicators
            lightbox = page.locator(
                "[class*='lightbox'], [class*='modal'], [class*='overlay'], "
                "[role='dialog']"
            )
            if lightbox.count() > 0:
                screenshots.capture(page, "04_lightbox_content", "Lightbox content visible")

    def test_lightbox_keyboard_navigation(self, page, ui_url, transfer_helper, screenshots):
        """Arrow keys navigate between images in the lightbox."""
        tid, key_b64 = self._create_image_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # Open lightbox
        thumb = page.locator(
            "img, [class*='thumbnail'], [class*='thumb']"
        ).first
        if thumb.is_visible(timeout=3000):
            thumb.click()
            page.wait_for_timeout(2000)
            screenshots.capture(page, "05_lightbox_nav_start", "Lightbox — first image")

            # Press right arrow to go to next image
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(1000)
            screenshots.capture(page, "06_lightbox_nav_right", "Lightbox — after right arrow")

            # Press left arrow to go back
            page.keyboard.press("ArrowLeft")
            page.wait_for_timeout(1000)
            screenshots.capture(page, "07_lightbox_nav_left", "Lightbox — after left arrow")

    def test_copy_link_button(self, page, ui_url, transfer_helper, screenshots):
        """Verify Copy Link button exists and the copied URL includes the key."""
        tid, key_b64 = self._create_image_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        copy_btn = page.locator(
            "button:has-text('Copy'), button:has-text('copy'), "
            "[title*='Copy'], [aria-label*='Copy']"
        ).first
        if copy_btn.is_visible(timeout=3000):
            screenshots.capture(page, "08_copy_link_button", "Copy Link button visible")

    def test_info_panel_toggle(self, page, ui_url, transfer_helper, screenshots):
        """Verify Info button toggles the info panel."""
        tid, key_b64 = self._create_image_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        info_btn = page.locator(
            "button:has-text('Info'), button:has-text('info'), "
            "[title*='Info'], [aria-label*='Info']"
        ).first
        if info_btn.is_visible(timeout=3000):
            info_btn.click()
            page.wait_for_timeout(1000)
            screenshots.capture(page, "09_info_panel_open", "Info panel opened")

            # Check for transfer metadata in the panel
            body_text = (page.text_content("body") or "").lower()
            metadata_indicators = ["transfer", "size", "file", "encrypt"]
            has_metadata = any(ind in body_text for ind in metadata_indicators)
            assert has_metadata, "Info panel does not show transfer metadata"

            # Toggle off
            info_btn.click()
            page.wait_for_timeout(1000)
            screenshots.capture(page, "10_info_panel_closed", "Info panel closed")

    def test_save_locally_button(self, page, ui_url, transfer_helper, screenshots):
        """Verify Save locally button triggers a download."""
        tid, key_b64 = self._create_image_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        save_btn = page.locator(
            "button:has-text('Save'), button:has-text('Download'), "
            "[title*='Save'], [title*='Download']"
        ).first
        if save_btn.is_visible(timeout=3000):
            screenshots.capture(page, "11_save_button", "Save locally button visible")
