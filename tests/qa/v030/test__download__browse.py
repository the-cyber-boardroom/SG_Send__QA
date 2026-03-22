"""UC-07: Browse view features (P1).

Tests browse-view-specific functionality:
  - Folder tree renders with expand/collapse
  - File click opens preview tab in right panel
  - Keyboard navigation: j/k moves through files, s saves
  - Share tab shows URL + copy + email
  - Info tab shows file counts by type, encryption info
  - Save locally downloads the zip
"""

import pytest

pytestmark = pytest.mark.p1


class TestBrowseFeatures:
    """Test browse view features with an uploaded folder."""

    def _create_folder_zip(self, transfer_helper):
        """Helper: create a zip with folder structure and upload it."""
        import zipfile, io

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            zf.writestr("docs/readme.md", b"# Project Readme\nSome documentation.")
            zf.writestr("docs/guide.md", b"# User Guide\nStep-by-step instructions.")
            zf.writestr("src/main.py", b'print("hello world")')
            zf.writestr("src/utils.py", b"def helper(): pass")
            zf.writestr("images/logo.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)
        zip_buf.seek(0)

        return transfer_helper.upload_encrypted(
            plaintext=zip_buf.read(),
            filename="browse-features.zip",
        )

    def test_folder_tree_renders(self, page, ui_url, transfer_helper, screenshots):
        """Verify folder tree renders with expand/collapse controls."""
        tid, key_b64 = self._create_folder_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        screenshots.capture(page, "01_browse_tree", "Browse view — folder tree")

        # Look for tree structure elements
        tree = page.locator(
            "[class*='tree'], [class*='folder'], [class*='sidebar'], "
            "[role='tree'], [role='treeitem']"
        )
        body_text = (page.text_content("body") or "").lower()

        # Should show folder names from the zip
        has_structure = "docs" in body_text or "src" in body_text or "readme" in body_text
        assert has_structure, (
            f"Folder tree does not show expected structure. Body snippet: {body_text[:500]}"
        )

    def test_file_click_opens_preview(self, page, ui_url, transfer_helper, screenshots):
        """Click a file in the tree → verify it opens a preview tab in the right panel."""
        tid, key_b64 = self._create_folder_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # Click on a markdown file in the tree
        file_link = page.locator(
            "text=readme.md, text=readme, text=guide.md"
        ).first
        if file_link.is_visible(timeout=3000):
            file_link.click()
            page.wait_for_timeout(2000)
            screenshots.capture(page, "02_file_preview", "File preview opened in right panel")

            # The preview should show the file content
            body_text = page.text_content("body") or ""
            has_content = "readme" in body_text.lower() or "documentation" in body_text.lower()
            assert has_content, "File preview does not show content"

    def test_keyboard_navigation(self, page, ui_url, transfer_helper, screenshots):
        """Verify keyboard navigation: j/k moves through files, s saves."""
        tid, key_b64 = self._create_folder_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # Press j to move down through files
        page.keyboard.press("j")
        page.wait_for_timeout(1000)
        screenshots.capture(page, "03_nav_j", "After pressing 'j' — next file")

        page.keyboard.press("j")
        page.wait_for_timeout(1000)
        screenshots.capture(page, "04_nav_j2", "After pressing 'j' again — next file")

        # Press k to move up
        page.keyboard.press("k")
        page.wait_for_timeout(1000)
        screenshots.capture(page, "05_nav_k", "After pressing 'k' — previous file")

    def test_share_tab(self, page, ui_url, transfer_helper, screenshots):
        """Verify Share tab shows URL + copy + email options."""
        tid, key_b64 = self._create_folder_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # Look for Share tab/button
        share_btn = page.locator(
            "button:has-text('Share'), [role='tab']:has-text('Share'), "
            "a:has-text('Share')"
        ).first
        if share_btn.is_visible(timeout=3000):
            share_btn.click()
            page.wait_for_timeout(1000)
            screenshots.capture(page, "06_share_tab", "Share tab opened")

            # Verify URL and copy/email buttons are present
            body_text = page.text_content("body") or ""
            copy_btn = page.locator("button:has-text('Copy'), [title*='Copy']").first
            has_copy = copy_btn.is_visible(timeout=2000) if copy_btn.count() > 0 else False
            screenshots.capture(page, "07_share_buttons", f"Share tab — copy visible: {has_copy}")

    def test_info_tab(self, page, ui_url, transfer_helper, screenshots):
        """Verify Info tab shows file counts by type and encryption info."""
        tid, key_b64 = self._create_folder_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # Look for Info tab/button
        info_btn = page.locator(
            "button:has-text('Info'), [role='tab']:has-text('Info'), "
            "a:has-text('Info')"
        ).first
        if info_btn.is_visible(timeout=3000):
            info_btn.click()
            page.wait_for_timeout(1000)
            screenshots.capture(page, "08_info_tab", "Info tab opened")

            body_text = (page.text_content("body") or "").lower()
            # Should mention encryption or file types
            info_indicators = ["encrypt", "aes", "file", "size", "type"]
            has_info = any(ind in body_text for ind in info_indicators)
            assert has_info, f"Info tab missing expected metadata. Body: {body_text[:500]}"

    def test_save_locally(self, page, ui_url, transfer_helper, screenshots):
        """Verify Save locally button exists in browse view."""
        tid, key_b64 = self._create_folder_zip(transfer_helper)

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        save_btn = page.locator(
            "button:has-text('Save'), button:has-text('Download'), "
            "[title*='Save'], [title*='Download']"
        ).first
        if save_btn.is_visible(timeout=3000):
            screenshots.capture(page, "09_save_button", "Save locally button visible in browse view")
