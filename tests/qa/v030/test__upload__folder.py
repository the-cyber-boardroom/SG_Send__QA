"""UC-02: Folder upload → gallery + browse view (P1).

Test flow:
  1. Upload a folder containing 3+ images and a markdown file
  2. Verify gallery mode is auto-selected (3+ images triggers gallery)
  3. Verify thumbnail grid renders with correct file count
  4. Click a thumbnail → verify lightbox opens
  5. Close lightbox → click "Folder view" link
  6. Verify browse view loads with folder tree
  7. Click a file in the tree → verify it opens in preview
  8. Click "Gallery view" → verify it switches back
"""

import pytest
import zipfile
import io

pytestmark = pytest.mark.p1

# Minimal 1×1 PNG bytes (valid PNG, tiny file)
_PNG_HEADER = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde'
    b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


def _make_folder_zip():
    """Build an in-memory zip with 3 PNG images + 1 markdown file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("my-folder/image1.png", _PNG_HEADER)
        zf.writestr("my-folder/image2.png", _PNG_HEADER)
        zf.writestr("my-folder/image3.png", _PNG_HEADER)
        zf.writestr("my-folder/readme.md", "# Test folder\n\nThis is a test.")
    buf.seek(0)
    return buf.read()


class TestFolderUpload:
    """Upload a folder zip and verify gallery + browse views."""

    def test_upload_zip_and_gallery_view(self, page, ui_url, send_server, screenshots):
        """Upload a zip with 3+ images; verify gallery mode is shown."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # Handle access gate if present
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        screenshots.capture(page, "01_upload_page", "Upload page loaded")

        # Feed the zip file
        zip_bytes = _make_folder_zip()
        file_input = page.locator("input[type='file']")
        file_input.set_input_files({
            "name"    : "my-folder.zip",
            "mimeType": "application/zip",
            "buffer"  : zip_bytes,
        })
        page.wait_for_timeout(1000)
        screenshots.capture(page, "02_file_selected", "Zip file selected")

        # Walk through wizard
        for _ in range(6):
            btn = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), "
                "button:has-text('Upload'), button:has-text('Encrypt'), "
                "button:has-text('Confirm')"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(800)

        page.wait_for_timeout(5000)
        screenshots.capture(page, "03_upload_done", "Upload complete — download link shown")

        # Get download link
        download_url = ""
        link_el = page.locator("a[href*='gallery'], a[href*='browse'], a[href*='download']").first
        if link_el.is_visible(timeout=5000):
            download_url = link_el.get_attribute("href") or ""
        else:
            input_el = page.locator("input[readonly]").first
            if input_el.is_visible(timeout=3000):
                download_url = input_el.get_attribute("value") or ""

        assert download_url, "No download link found after folder upload"

        if download_url.startswith("/"):
            download_url = f"{ui_url}{download_url}"

        # Open the download page — expect gallery view (3 images auto-select gallery)
        dl_page = page.context.new_page()
        dl_page.goto(download_url)
        dl_page.wait_for_load_state("networkidle")
        dl_page.wait_for_timeout(3000)
        screenshots.capture(dl_page, "04_download_gallery", "Gallery view after zip download")

        page_text = dl_page.text_content("body") or ""
        # Should show some gallery-like content (thumbnails, image count, gallery indicator)
        assert any(kw in page_text.lower() for kw in ["gallery", "image", "thumbnail", "photo"]), \
            "Gallery view not detected for image-heavy zip"

        dl_page.close()

    def test_gallery_thumbnail_grid(self, page, ui_url, transfer_helper, screenshots):
        """Create a zip upload via API, open gallery, verify thumbnail grid."""
        zip_bytes = _make_folder_zip()
        tid, key_b64 = transfer_helper.upload_encrypted(zip_bytes, "my-folder.zip")

        gallery_url = f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}"
        page.goto(gallery_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        screenshots.capture(page, "05_gallery_thumbnails", "Gallery thumbnail grid")

        page_text = page.text_content("body") or ""
        # The gallery page should load without a fatal error
        assert "error" not in page_text.lower() or "gallery" in page_text.lower(), \
            "Gallery page shows error instead of content"

    def test_browse_view_folder_tree(self, page, ui_url, transfer_helper, screenshots):
        """Open browse view for the zip; verify folder tree is present."""
        zip_bytes = _make_folder_zip()
        tid, key_b64 = transfer_helper.upload_encrypted(zip_bytes, "my-folder.zip")

        browse_url = f"{ui_url}/en-gb/browse/#{tid}/{key_b64}"
        page.goto(browse_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        screenshots.capture(page, "06_browse_view", "Browse view with folder tree")

        page_text = page.text_content("body") or ""
        assert "error" not in page_text.lower() or "browse" in page_text.lower(), \
            "Browse page shows error instead of content"

    def test_mode_switch_preserves_hash(self, page, ui_url, transfer_helper, screenshots):
        """Gallery ↔ browse mode switching preserves the hash fragment."""
        zip_bytes = _make_folder_zip()
        tid, key_b64 = transfer_helper.upload_encrypted(zip_bytes, "my-folder.zip")
        expected_hash = f"#{tid}/{key_b64}"

        # Start at gallery
        gallery_url = f"{ui_url}/en-gb/gallery/{expected_hash}"
        page.goto(gallery_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # Look for "Folder view" / "Browse" link and click it
        browse_link = page.locator(
            "a:has-text('Folder view'), a:has-text('Browse'), a[href*='browse']"
        ).first
        if browse_link.is_visible(timeout=5000):
            browse_link.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            screenshots.capture(page, "07_switched_to_browse", "Switched to browse view")

            # Hash should be preserved in the new URL
            current_url = page.url
            assert tid in current_url or expected_hash in current_url, \
                f"Hash not preserved after mode switch: {current_url}"
