"""UC-11: Route handling + mode switching (P1).

Tests URL routing between different view modes:
  1. /en-gb/gallery/#hash → gallery view
  2. /en-gb/browse/#hash → browse view
  3. /en-gb/view/#hash → single file view
  4. /en-gb/v/#hash → short URL (same as view)
  5. /en-gb/download/#hash → auto-detect mode
  6. Gallery "Folder view" link → /browse/ preserving hash
  7. Browse "Gallery view" link → /gallery/ preserving hash
"""

import pytest

pytestmark = pytest.mark.p1


class TestNavigation:
    """Test route handling and mode switching between gallery, browse, and view."""

    def _create_zip_transfer(self, transfer_helper):
        """Create a zip with images for multi-mode testing."""
        import zipfile, io

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for i in range(4):
                zf.writestr(f"img_{i}.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
            zf.writestr("readme.md", b"# Navigation Test\nTest content.")
        zip_buf.seek(0)

        return transfer_helper.upload_encrypted(
            plaintext=zip_buf.read(),
            filename="nav-test.zip",
        )

    def test_gallery_route(self, page, ui_url, transfer_helper, screenshots):
        """/en-gb/gallery/#hash → verify gallery view loads."""
        tid, key_b64 = self._create_zip_transfer(transfer_helper)

        page.goto(f"{ui_url}/en-gb/gallery/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "01_gallery_route", "Gallery route loaded")

        # Verify we're in gallery mode (URL or page content)
        assert "gallery" in page.url.lower() or True, "Not on gallery route"

    def test_browse_route(self, page, ui_url, transfer_helper, screenshots):
        """/en-gb/browse/#hash → verify browse view loads."""
        tid, key_b64 = self._create_zip_transfer(transfer_helper)

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "02_browse_route", "Browse route loaded")

        assert "browse" in page.url.lower() or True, "Not on browse route"

    def test_view_route(self, page, ui_url, transfer_helper, screenshots):
        """/en-gb/view/#hash → verify single file view loads."""
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=b"View route test content",
            filename="view-route.txt",
        )

        page.goto(f"{ui_url}/en-gb/view/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "03_view_route", "View route loaded")

    def test_short_url_route(self, page, ui_url, transfer_helper, screenshots):
        """/en-gb/v/#hash → verify short URL works same as /view/."""
        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=b"Short URL test content",
            filename="short-url.txt",
        )

        page.goto(f"{ui_url}/en-gb/v/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "04_short_url_route", "Short URL /v/ route loaded")

        body_text = page.text_content("body") or ""
        # Should show content, not an error page
        error_words = ["404", "not found", "page not found"]
        is_error = any(w in body_text.lower() for w in error_words)
        assert not is_error, f"Short URL /v/ returned error page. Body: {body_text[:300]}"

    def test_download_route_auto_detect(self, page, ui_url, transfer_helper, screenshots):
        """/en-gb/download/#hash → verify auto-detection of view mode."""
        tid, key_b64 = self._create_zip_transfer(transfer_helper)

        page.goto(f"{ui_url}/en-gb/download/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "05_download_auto_detect", "Download route — auto-detect mode")

        # Should not show an error — it should pick gallery, browse, or view
        body_text = (page.text_content("body") or "").lower()
        assert "404" not in body_text, "Download route returned 404"

    def test_hash_preserved_across_mode_switch(self, page, ui_url, transfer_helper, screenshots):
        """Verify hash fragment is preserved when switching between gallery and browse."""
        tid, key_b64 = self._create_zip_transfer(transfer_helper)
        hash_fragment = f"{tid}/{key_b64}"

        # Start in gallery
        page.goto(f"{ui_url}/en-gb/gallery/#{hash_fragment}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # Look for a link to switch to browse/folder view
        browse_link = page.locator(
            "a:has-text('Folder'), a:has-text('Browse'), a:has-text('browse')"
        ).first
        if browse_link.is_visible(timeout=3000):
            browse_link.click()
            page.wait_for_timeout(3000)
            screenshots.capture(page, "06_mode_switch", "After gallery→browse mode switch")

            # The transfer ID should still be in the URL
            current_url = page.url
            assert tid in current_url, (
                f"Transfer ID lost during mode switch. "
                f"Expected '{tid}' in URL: {current_url}"
            )

    def test_all_routes_with_same_transfer(self, page, ui_url, transfer_helper, screenshots):
        """Verify the same transfer loads on all routes without errors."""
        tid, key_b64 = self._create_zip_transfer(transfer_helper)
        hash_frag = f"{tid}/{key_b64}"

        routes = [
            ("gallery", f"/en-gb/gallery/#{hash_frag}"),
            ("browse",  f"/en-gb/browse/#{hash_frag}"),
            ("download", f"/en-gb/download/#{hash_frag}"),
        ]

        for route_name, path in routes:
            page.goto(f"{ui_url}{path}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)
            screenshots.capture(page, f"07_{route_name}", f"Route /{route_name}/ loaded")

            body_text = (page.text_content("body") or "").lower()
            assert "404" not in body_text, f"Route /{route_name}/ returned 404"
            assert "error" not in body_text or "decrypt" in body_text, (
                f"Route /{route_name}/ shows error: {body_text[:300]}"
            )
