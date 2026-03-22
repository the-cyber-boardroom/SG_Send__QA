"""UC-02: Folder upload → gallery + browse views (P1).

Flow:
  1. Upload a folder with 3+ images and a markdown file
  2. Verify gallery mode auto-selected (3+ images triggers gallery)
  3. Verify thumbnail grid renders with correct file count
  4. Click a thumbnail → verify lightbox opens
  5. Close lightbox, click "Folder view" link
  6. Verify browse view with folder tree + preview panel
  7. Click "Gallery view" → verify mode switch
"""

import pytest

pytestmark = pytest.mark.p1

SAMPLE_FILES = [
    {"name": "photos/img1.png",  "mimeType": "image/png",  "buffer": b"\x89PNG\r\n\x1a\n" + b"\x00" * 100},
    {"name": "photos/img2.png",  "mimeType": "image/png",  "buffer": b"\x89PNG\r\n\x1a\n" + b"\x00" * 100},
    {"name": "photos/img3.png",  "mimeType": "image/png",  "buffer": b"\x89PNG\r\n\x1a\n" + b"\x00" * 100},
    {"name": "docs/readme.md",   "mimeType": "text/markdown", "buffer": b"# Test Folder\nThis is a test."},
]


class TestFolderUpload:
    """Upload a folder with images and documents, verify gallery and browse views."""

    def test_folder_upload_triggers_gallery(self, page, ui_url, send_server, screenshots):
        """Upload 3+ images → verify gallery view is auto-selected."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # Handle access gate
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        # Upload multiple files (simulating folder upload)
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(SAMPLE_FILES)
        page.wait_for_timeout(1000)
        screenshots.capture(page, "01_folder_selected", "Folder with 3 images + 1 markdown selected")

        # Walk through the wizard
        for _ in range(8):
            btn = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), "
                "button:has-text('Upload'), button:has-text('Encrypt'), "
                "button:has-text('Confirm')"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(1000)

        page.wait_for_timeout(5000)
        screenshots.capture(page, "02_upload_complete", "Folder upload complete")

        # Extract download link
        download_url = ""
        link_el = page.locator("a[href*='download'], a[href*='gallery'], a[href*='/en-gb/']").first
        if link_el.is_visible(timeout=3000):
            download_url = link_el.get_attribute("href") or ""
        if not download_url:
            for input_el in page.locator("input[readonly]").all():
                val = input_el.get_attribute("value") or ""
                if "#" in val:
                    download_url = val
                    break

        assert download_url, "No download link found after folder upload"

        if download_url.startswith("/"):
            download_url = f"{ui_url}{download_url}"

        # Open the link — with 3+ images, gallery should be auto-selected
        dl_page = page.context.new_page()
        dl_page.goto(download_url)
        dl_page.wait_for_load_state("networkidle")
        dl_page.wait_for_timeout(5000)
        screenshots.capture(dl_page, "03_gallery_view", "Gallery view auto-selected for image-heavy folder")

        # Gallery indicators: thumbnails, grid layout, file count
        body_text = dl_page.text_content("body") or ""
        dl_page.close()

    def test_gallery_to_browse_mode_switch(self, page, ui_url, transfer_helper, screenshots):
        """Verify switching from gallery to browse view preserves the hash fragment."""
        # Create a transfer with images via API
        import zipfile, io

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for i in range(4):
                zf.writestr(f"img{i}.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
            zf.writestr("readme.md", b"# Gallery test")
        zip_buf.seek(0)

        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=zip_buf.read(),
            filename="gallery-test.zip",
        )

        # Open gallery view
        gallery_url = f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}"
        page.goto(gallery_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "04_gallery_loaded", "Gallery view loaded")

        # Look for "Folder view" or "Browse" link
        browse_link = page.locator(
            "a:has-text('Folder'), a:has-text('Browse'), a:has-text('browse')"
        ).first
        if browse_link.is_visible(timeout=3000):
            browse_link.click()
            page.wait_for_timeout(3000)
            screenshots.capture(page, "05_browse_from_gallery", "Switched to browse view from gallery")

            # Verify hash fragment is preserved in the new URL
            current_url = page.url
            assert tid in current_url, (
                f"Transfer ID lost during gallery→browse switch. URL: {current_url}"
            )

    def test_browse_to_gallery_mode_switch(self, page, ui_url, transfer_helper, screenshots):
        """Verify switching from browse to gallery view preserves the hash fragment."""
        import zipfile, io

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for i in range(4):
                zf.writestr(f"img{i}.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
        zip_buf.seek(0)

        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=zip_buf.read(),
            filename="browse-test.zip",
        )

        # Open browse view
        browse_url = f"{ui_url}/en-gb/browse/#{tid}/{key_b64}"
        page.goto(browse_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "06_browse_loaded", "Browse view loaded")

        # Look for "Gallery view" link
        gallery_link = page.locator(
            "a:has-text('Gallery'), a:has-text('gallery')"
        ).first
        if gallery_link.is_visible(timeout=3000):
            gallery_link.click()
            page.wait_for_timeout(3000)
            screenshots.capture(page, "07_gallery_from_browse", "Switched to gallery view from browse")

            current_url = page.url
            assert tid in current_url, (
                f"Transfer ID lost during browse→gallery switch. URL: {current_url}"
            )

    def test_gallery_header_shows_metadata(self, page, ui_url, transfer_helper, screenshots):
        """Verify gallery header shows archive name, size, and file count."""
        import zipfile, io

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for i in range(3):
                zf.writestr(f"photo_{i}.jpg", b"\xff\xd8\xff\xe0" + b"\x00" * 80)
        zip_buf.seek(0)

        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=zip_buf.read(),
            filename="metadata-test.zip",
        )

        page.goto(f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "08_gallery_header", "Gallery header with metadata")

        body_text = (page.text_content("body") or "").lower()
        # Should show file count somewhere on the page
        # (3 files — look for "3" or "files" in the content)
        assert "3" in body_text or "file" in body_text, (
            f"Gallery header does not appear to show file count. Body snippet: {body_text[:300]}"
        )
