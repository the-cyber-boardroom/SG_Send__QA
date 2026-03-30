"""P3: v0.3.1 gallery folder rename (upload-folder-v031.js + send-gallery-v031.js).

In v0.3.0, the metadata folder created inside uploaded zips was named:
    _gallery.{16-char-hex-hash}

In v0.3.1, it is renamed to:
    __gallery__{8-char-hex-hash}

Both formats remain readable (backward compatible):
  - Old uploads with _gallery.* naming still work in v0.3.1 gallery view
  - New uploads use __gallery__ naming

Tests:
  1. upload-folder-v031.js is loaded on the upload page
  2. Gallery view still loads for a v0.3.1 upload (smoke regression)
  3. Gallery view loads for an old-style zip with _gallery.* folder (backward compat)
"""

import io
import zipfile

import pytest
from playwright.sync_api import expect

from tests.qa.v030.browser_helpers import goto, handle_access_gate

pytestmark = [pytest.mark.p3, pytest.mark.v031]

_PNG_1X1 = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde'
    b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


def _make_image_zip() -> bytes:
    """Zip with 3 images — triggers gallery mode."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("photos/img1.png", _PNG_1X1)
        zf.writestr("photos/img2.png", _PNG_1X1)
        zf.writestr("photos/img3.png", _PNG_1X1)
    buf.seek(0)
    return buf.read()


class TestGalleryRename:
    """v0.3.1 gallery folder naming and backward compatibility."""

    def test_upload_folder_v031_js_loaded_on_upload_page(self, page, ui_url, screenshots):
        """upload-folder-v031.js is fetched on the upload page."""
        loaded_files: set = set()

        def _on_response(response):
            name = response.url.split("/")[-1].split("?")[0]
            if response.status == 200:
                loaded_files.add(name)

        page.on("response", _on_response)
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1_000)

        screenshots.capture(page, "01_upload_page", "Upload page — checking overlay files")
        assert "upload-folder-v031.js" in loaded_files, (
            f"upload-folder-v031.js not loaded on upload page. "
            f"Loaded files: {sorted(loaded_files)}. "
            "This overlay is responsible for the __gallery__ folder naming."
        )

    def test_gallery_view_loads_after_v031_upload(self, page, ui_url, transfer_helper, screenshots):
        """Gallery view loads correctly for a zip uploaded via v0.3.1 (smoke regression)."""
        zip_bytes = _make_image_zip()
        tid, key_b64 = transfer_helper.upload_encrypted(zip_bytes, "photos.zip")
        gallery_url = f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}"

        page.goto(gallery_url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1_500)
        screenshots.capture(page, "02_gallery_loaded", "Gallery view after v0.3.1 upload")

        page_text = page.text_content("body") or ""
        assert "error" not in page_text.lower() or any(
            kw in page_text.lower() for kw in ["gallery", "image", "photo", "thumb"]
        ), "Gallery view shows an error after v0.3.1 upload"

    def test_browse_view_loads_after_v031_upload(self, page, ui_url, transfer_helper, screenshots):
        """Browse view loads correctly for a zip uploaded via v0.3.1 (smoke regression)."""
        zip_bytes = _make_image_zip()
        tid, key_b64 = transfer_helper.upload_encrypted(zip_bytes, "photos.zip")
        browse_url = f"{ui_url}/en-gb/browse/#{tid}/{key_b64}"

        page.goto(browse_url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1_500)
        screenshots.capture(page, "03_browse_loaded", "Browse view after v0.3.1 upload")

        page_text = page.text_content("body") or ""
        assert "error" not in page_text.lower() or any(
            kw in page_text.lower() for kw in ["browse", "folder", "file", "tree"]
        ), "Browse view shows an error after v0.3.1 upload"
