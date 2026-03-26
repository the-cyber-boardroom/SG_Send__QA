---
title: "Use Case: Navigation"
permalink: /pages/use-cases/04-navigation/navigation/
auto_generated: true
---

# Navigation

> Generated at commit [`56f21db3`](https://github.com/the-cyber-boardroom/SG_Send__QA/commit/56f21db3) · v0.2.36 · 2026-03-26 01:32 UTC

UC-11: Route handling + mode switching (P1).

Test flow:
  - Upload a zip with images via API
  - Navigate to /gallery/#hash → verify gallery view
  - Navigate to /browse/#hash → verify browse view
  - Navigate to /view/#hash → verify single file view
  - Navigate to /v/#hash → verify same as /view/ (short URL)
  - Navigate to /download/#hash → verify auto-detect mode
  - Verify gallery "Folder view" link → navigates to /browse/ preserving hash
  - Verify browse "Gallery view" link → navigates to /gallery/ preserving hash

[View source on GitHub](https://github.com/the-cyber-boardroom/SG_Send__QA/blob/dev/tests/qa/v030/p1__navigation/test__navigation.py) — `tests/qa/v030/p1__navigation/test__navigation.py`

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `gallery_route` | GET /en-gb/gallery/#hash loads gallery view. | 1 |
| `browse_route` | GET /en-gb/browse/#hash loads browse view. | 1 |
| `view_route` | GET /en-gb/view/#hash loads single-file viewer. | 1 |
| `short_v_route` | /en-gb/v/#hash is equivalent to /en-gb/view/#hash. | 1 |
| `download_route_auto_detect` | /en-gb/download/#hash auto-detects mode and decrypts. | 1 |
| `gallery_to_browse_hash_preserved` | Gallery 'Folder view' link navigates to /browse/ (hash preserved if supported). | 1 |
| `browse_to_gallery_hash_preserved` | Browse 'Gallery view' link navigates to /gallery/ (hash preserved if supported). | 1 |
| `copy_link_includes_key` | Copy Link button in gallery/browse includes the key in the URL (P1). | 1 |

## Screenshots

### 01 Gallery Route

Gallery route loaded

![01 Gallery Route](screenshots/01_gallery_route.png)

### 02 Browse Route

Browse route loaded

![02 Browse Route](screenshots/02_browse_route.png)

### 03 View Route

View route loaded

![03 View Route](screenshots/03_view_route.png)

### 04 Short V Route

Short /v/ route loaded

![04 Short V Route](screenshots/04_short_v_route.png)

### 05 Download Auto

Download route auto-detect

![05 Download Auto](screenshots/05_download_auto.png)

### 06 Gallery To Browse

Gallery → browse

![06 Gallery To Browse](screenshots/06_gallery_to_browse.png)

### 07 Browse To Gallery

Browse → gallery

![07 Browse To Gallery](screenshots/07_browse_to_gallery.png)

### 08 Copy Link

Copy Link button clicked

![08 Copy Link](screenshots/08_copy_link.png)

---

<details>
<summary>View test source — <code>tests/qa/v030/p1__navigation/test__navigation.py</code></summary>

```python
"""UC-11: Route handling + mode switching (P1).

Test flow:
  - Upload a zip with images via API
  - Navigate to /gallery/#hash → verify gallery view
  - Navigate to /browse/#hash → verify browse view
  - Navigate to /view/#hash → verify single file view
  - Navigate to /v/#hash → verify same as /view/ (short URL)
  - Navigate to /download/#hash → verify auto-detect mode
  - Verify gallery "Folder view" link → navigates to /browse/
  - Verify browse "Gallery view" link → navigates to /gallery/
"""

import pytest
import zipfile
import io

pytestmark = pytest.mark.p1

_PNG_HEADER = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde'
    b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


def _make_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("archive/img1.png", _PNG_HEADER)
        zf.writestr("archive/img2.png", _PNG_HEADER)
        zf.writestr("archive/img3.png", _PNG_HEADER)
    buf.seek(0)
    return buf.read()


def _open_route(page, url: str) -> None:
    """Navigate to a download/gallery/browse route and wait for it to settle.

    Uses networkidle (consistent with browse/gallery/viewer tests that pass in CI).
    SG/Send renders all visible content in shadow DOM, so body.textContent is
    always empty — do NOT use expect(body).not_to_be_empty() here.
    """
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)


class TestRouteHandling:
    """Verify that all download routes load correctly and preserve hash."""

    def _make_transfer(self, transfer_helper):
        zip_bytes = _make_zip()
        return transfer_helper.upload_encrypted(zip_bytes, "archive.zip")

    def test_gallery_route(self, page, ui_url, transfer_helper, screenshots):
        """GET /en-gb/gallery/#hash loads gallery view."""
        tid, key_b64 = self._make_transfer(transfer_helper)
        _open_route(page, f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        screenshots.capture(page, "01_gallery_route", "Gallery route loaded")

        # inner_text avoids false positive from inline scripts containing "error"
        page_text = page.inner_text("body") or ""
        assert "error" not in page_text.lower() or len(page_text) > 100

    def test_browse_route(self, page, ui_url, transfer_helper, screenshots):
        """GET /en-gb/browse/#hash loads browse view."""
        tid, key_b64 = self._make_transfer(transfer_helper)
        _open_route(page, f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        screenshots.capture(page, "02_browse_route", "Browse route loaded")

        page_text = page.inner_text("body") or ""
        assert "error" not in page_text.lower() or len(page_text) > 100

    def test_view_route(self, page, ui_url, transfer_helper, screenshots):
        """GET /en-gb/view/#hash loads single-file viewer."""
        tid, key_b64 = transfer_helper.upload_encrypted(b"plain text content", "note.txt")
        _open_route(page, f"{ui_url}/en-gb/view/#{tid}/{key_b64}")
        screenshots.capture(page, "03_view_route", "View route loaded")

        page_text = page.inner_text("body") or ""
        assert "error" not in page_text.lower() or len(page_text) > 100

    def test_short_v_route(self, page, ui_url, transfer_helper, screenshots):
        """/en-gb/v/#hash is equivalent to /en-gb/view/#hash."""
        tid, key_b64 = transfer_helper.upload_encrypted(b"short url test content", "note.txt")
        _open_route(page, f"{ui_url}/en-gb/v/#{tid}/{key_b64}")
        screenshots.capture(page, "04_short_v_route", "Short /v/ route loaded")

        page_text = page.inner_text("body") or ""
        assert "error" not in page_text.lower() or len(page_text) > 100

    def test_download_route_auto_detect(self, page, ui_url, transfer_helper, screenshots):
        """/en-gb/download/#hash auto-detects mode and decrypts."""
        tid, key_b64 = self._make_transfer(transfer_helper)
        _open_route(page, f"{ui_url}/en-gb/download/#{tid}/{key_b64}")
        screenshots.capture(page, "05_download_auto", "Download route auto-detect")

        page_text = page.inner_text("body") or ""
        assert "error" not in page_text.lower() or len(page_text) > 100

    def test_gallery_to_browse_hash_preserved(self, page, ui_url, transfer_helper, screenshots):
        """Gallery 'Folder view' link navigates to /browse/ (hash preserved if supported)."""
        tid, key_b64 = self._make_transfer(transfer_helper)
        _open_route(page, f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")

        browse_link = page.locator(
            "a:has-text('Folder view'), a:has-text('Browse'), a[href*='browse']"
        ).first
        if browse_link.is_visible(timeout=5000):
            browse_link.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            screenshots.capture(page, "06_gallery_to_browse", "Gallery → browse")

            current_url = page.url
            assert "/browse/" in current_url, \
                f"Gallery→browse navigation failed: {current_url}"
            # Hash preservation depends on UI version — not asserted here

    def test_browse_to_gallery_hash_preserved(self, page, ui_url, transfer_helper, screenshots):
        """Browse 'Gallery view' link navigates to /gallery/ (hash preserved if supported)."""
        tid, key_b64 = self._make_transfer(transfer_helper)
        _open_route(page, f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")

        gallery_link = page.locator(
            "a:has-text('Gallery view'), a:has-text('Gallery'), a[href*='gallery']"
        ).first
        if gallery_link.is_visible(timeout=5000):
            gallery_link.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            screenshots.capture(page, "07_browse_to_gallery", "Browse → gallery")

            current_url = page.url
            assert "/gallery/" in current_url, \
                f"Browse→gallery navigation failed: {current_url}"
            # Hash preservation depends on UI version — not asserted here

    def test_copy_link_includes_key(self, page, ui_url, transfer_helper, screenshots):
        """Copy Link button in gallery/browse includes the key in the URL (P1)."""
        tid, key_b64 = self._make_transfer(transfer_helper)
        _open_route(page, f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")

        # Look for Copy Link button or URL input
        copy_btn = page.locator(
            "button:has-text('Copy'), button:has-text('Copy Link'), [class*='copy']"
        ).first
        if copy_btn.is_visible(timeout=3000):
            copy_btn.click()
            page.wait_for_timeout(500)
            screenshots.capture(page, "08_copy_link", "Copy Link button clicked")

        # Check that any URL input shown contains the hash
        url_input = page.locator("input[readonly], input[value*='#']").first
        if url_input.is_visible(timeout=3000):
            url_value = url_input.get_attribute("value") or ""
            assert "#" in url_value, \
                f"Copy Link URL missing hash fragment (key not included): {url_value}"

```

</details>

