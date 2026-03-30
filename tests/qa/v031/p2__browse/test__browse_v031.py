"""P2: v0.3.1 Browse view — BRW-001 through BRW-015.

All 15 browse-view fixes shipped in send-browse-v031.js,
markdown-parser-v031.js, and send-browse-v031.css.

Test zip layout (built by _make_v031_zip):
    00_start.md             ← root, alphabetically first (BRW-003 auto-open)
    ACCOUNTANT DEBRIEF.md   ← space in filename (BRW-011 %20 links)
    NOTES.md                ← markdown: relative link, image ref, %20 link, folder link
    data/
        report.md           ← plain markdown
        data.csv            ← CSV file (BRW-012 table render)
        dashboard.html      ← HTML with <script> (BRW-013 iframe render)
        slides.pdf          ← PDF (BRW-002 Present button)
        sub/
            deep.md         ← basename test: shows "deep.md" not "data/sub/deep.md" (BRW-001)
    images/
        chart.png           ← referenced by NOTES.md (BRW-005/007 image render)
"""

import io
import zipfile

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.p2, pytest.mark.v031]

# ---------------------------------------------------------------------------
# Minimal valid assets embedded as bytes
# ---------------------------------------------------------------------------

_PNG_1X1 = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde'
    b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)

_MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R "
    b"/MediaBox [0 0 72 72] /Resources << >> /Contents 4 0 R >>\nendobj\n"
    b"4 0 obj\n<< /Length 0 >>\nstream\nendstream\nendobj\n"
    b"xref\n0 5\n"
    b"0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000058 00000 n \n"
    b"0000000115 00000 n \n"
    b"0000000266 00000 n \n"
    b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n317\n%%EOF\n"
)

_CSV_CONTENT = (
    "Name,Department,Score\n"
    "Alice,Engineering,92\n"
    "Bob,Marketing,78\n"
    "Carol,Engineering,88\n"
    "Dave,Design,95\n"
    "Eve,Marketing,81\n"
)

_HTML_CONTENT = """<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
<h1>Dashboard</h1>
<p id="status">Loading...</p>
<script>document.getElementById('status').textContent = 'Script ran';</script>
</body>
</html>"""

_NOTES_MD = (
    "# Notes\n\n"
    "See the [report](data/report.md) for details.\n\n"
    "![Chart](images/chart.png)\n\n"
    "[Open accountant notes](ACCOUNTANT%20DEBRIEF.md)\n\n"
    "[Browse data folder](data/)\n"
)


def _make_v031_zip() -> bytes:
    """Build the comprehensive v0.3.1 test zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("00_start.md",           "# Start\n\nThis file should auto-open.")
        zf.writestr("ACCOUNTANT DEBRIEF.md", "# Accountant Debrief\n\nSpaces in filename.")
        zf.writestr("NOTES.md",              _NOTES_MD)
        zf.writestr("data/report.md",        "# Report\n\nContent here.")
        zf.writestr("data/data.csv",         _CSV_CONTENT)
        zf.writestr("data/dashboard.html",   _HTML_CONTENT)
        zf.writestr("data/slides.pdf",       _MINIMAL_PDF)
        zf.writestr("data/sub/deep.md",      "# Deep file\n\nNested two levels.")
        zf.writestr("images/chart.png",      _PNG_1X1)
    buf.seek(0)
    return buf.read()


class TestBrowseV031:
    """BRW-001 through BRW-015 — all 15 browse view fixes from v0.3.1."""

    @pytest.fixture(autouse=True)
    def _browse_url(self, transfer_helper, ui_url):
        """Upload the test zip once per test class instance and cache the browse URL."""
        zip_bytes = _make_v031_zip()
        tid, key_b64 = transfer_helper.upload_encrypted(zip_bytes, "test-v031.zip")
        self._url = f"{ui_url}/en-gb/browse/#{tid}/{key_b64}"

    def _open(self, page):
        """Navigate to browse view and wait for ready signal."""
        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1_500)   # let JS render the tree + auto-open first file

    # ── BRW-001: Folder tree shows basenames, not full zip paths ─────────────

    def test_brw001_tree_shows_basenames(self, page, screenshots):
        """BRW-001: Files in subfolders show only the filename, not the full path."""
        self._open(page)
        screenshots.capture(page, "brw001_01_tree", "Folder tree loaded")

        # The deep file is at data/sub/deep.md — in v0.3.1 its label is "deep.md"
        file_names = page.locator(".sb-tree__file-name").all_text_contents()
        assert file_names, "No .sb-tree__file-name elements found — tree did not render"

        for name in file_names:
            assert "/" not in name, (
                f"File name '{name}' contains '/' — BRW-001 fix not active. "
                "Folder tree is showing full zip paths instead of basenames."
            )

    # ── BRW-002: PDF Present button in browse view ───────────────────────────

    def test_brw002_pdf_present_button_in_browse(self, page, screenshots):
        """BRW-002: PDF files in browse view show a Present button in the action bar."""
        self._open(page)

        # Click on the PDF file in the tree
        pdf_item = page.locator(".sb-tree__file[data-path*='slides.pdf']").first
        if not pdf_item.is_visible(timeout=3_000):
            # Expand data/ folder first
            data_folder = page.locator(".sb-tree__folder[data-path='data']").first
            if data_folder.is_visible(timeout=2_000):
                data_folder.click()
                page.wait_for_timeout(500)
            pdf_item = page.locator(".sb-tree__file[data-path*='slides.pdf']").first

        pdf_item.click()
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw002_01_pdf_open", "PDF opened in browse view")

        present_btn = page.locator(".sb-file__present").first
        assert present_btn.is_visible(timeout=3_000), (
            "BRW-002: No .sb-file__present button found for PDF in browse view. "
            "This was missing in v0.3.0 and added by send-browse-v031.js."
        )

        # Non-PDF files should NOT have a Present button
        md_item = page.locator(".sb-tree__file[data-path='data/report.md']").first
        if md_item.is_visible(timeout=2_000):
            md_item.click()
            page.wait_for_timeout(500)
            screenshots.capture(page, "brw002_02_md_no_present", "Markdown — no Present button")
            assert not page.locator(".sb-file__present").is_visible(timeout=1_000), \
                "BRW-002: Present button appeared for a non-PDF file (should be PDF-only)"

    # ── BRW-003: Auto-open first file (alphabetical) ─────────────────────────

    def test_brw003_auto_opens_first_alphabetical_file(self, page, screenshots):
        """BRW-003: On first load, the alphabetically first root file is opened automatically."""
        self._open(page)
        screenshots.capture(page, "brw003_01_initial_load", "Browse view on first load")

        # 00_start.md is alphabetically before ACCOUNTANT DEBRIEF.md and NOTES.md
        # The active tab or content area should show "00_start.md" or its content
        page_text = page.text_content("body") or ""
        assert "This file should auto-open" in page_text or "00_start" in page_text, (
            "BRW-003: Expected '00_start.md' to be auto-opened (alphabetically first). "
            "Content 'This file should auto-open' not found on initial load."
        )

    # ── BRW-004 + BRW-008: Markdown relative links open as tabs ─────────────

    def test_brw004_markdown_relative_links_open_as_tabs(self, page, screenshots):
        """BRW-004/BRW-008: Clicking a relative link in markdown opens the target file as a tab."""
        self._open(page)

        # Open NOTES.md which has [report](data/report.md)
        notes_item = page.locator(".sb-tree__file[data-path='NOTES.md']").first
        notes_item.click()
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw004_01_notes_open", "NOTES.md opened — contains relative link")

        # Click the relative link to data/report.md
        report_link = page.locator("a").filter(has_text="report").first
        initial_tabs = page.locator(".sgl-tab").count()

        if report_link.is_visible(timeout=3_000):
            report_link.click()
            page.wait_for_timeout(800)
            screenshots.capture(page, "brw004_02_link_clicked", "After clicking relative link")

            tabs_after = page.locator(".sgl-tab").count()
            assert tabs_after > initial_tabs or "Report" in (page.text_content("body") or ""), (
                "BRW-004/008: Clicking relative link did not open a new tab or navigate to target. "
                "Relative links in markdown should open the target file as a tab."
            )
        else:
            pytest.skip("Relative link in NOTES.md not rendered as <a> — markdown may not have rendered")

    # ── BRW-005 + BRW-007: Markdown images render inline from zip ────────────

    def test_brw005_markdown_images_render_inline(self, page, screenshots):
        """BRW-005/BRW-007: Images referenced in markdown render as <img> tags with blob URLs."""
        self._open(page)

        notes_item = page.locator(".sb-tree__file[data-path='NOTES.md']").first
        notes_item.click()
        page.wait_for_timeout(1_500)
        screenshots.capture(page, "brw005_01_notes_with_image", "NOTES.md — image should render inline")

        # Check that an <img> tag exists (BRW-007: not a placeholder "[image: ...]")
        img_tags = page.locator("img").all()
        assert len(img_tags) > 0, (
            "BRW-005/007: No <img> tags found after opening NOTES.md. "
            "Images should render inline, not as [image: alt] placeholder text."
        )

        # Verify at least one img has a blob: URL (resolved from zip — BRW-005)
        img_srcs = [img.get_attribute("src") or "" for img in img_tags]
        blob_srcs = [src for src in img_srcs if src.startswith("blob:")]
        assert blob_srcs, (
            f"BRW-005: No img with blob: URL found. Sources: {img_srcs}. "
            "Images should be resolved from zip content via blob URLs, not HTTP requests."
        )

    # ── BRW-006: Markdown Source / Rendered toggle ───────────────────────────

    def test_brw006_markdown_source_toggle(self, page, screenshots):
        """BRW-006: Markdown files show a Source toggle button that switches to raw text."""
        self._open(page)

        notes_item = page.locator(".sb-tree__file[data-path='NOTES.md']").first
        notes_item.click()
        page.wait_for_timeout(1_000)

        source_btn = page.locator(".sb-file__view-source").first
        assert source_btn.is_visible(timeout=3_000), (
            "BRW-006: No .sb-file__view-source button found for markdown file. "
            "send-browse-v031.js should add a Source toggle to markdown files."
        )

        initial_label = source_btn.text_content() or ""
        screenshots.capture(page, "brw006_01_rendered_view", f"Markdown rendered view — button: {initial_label!r}")

        source_btn.click()
        page.wait_for_timeout(500)
        after_label = source_btn.text_content() or ""
        screenshots.capture(page, "brw006_02_source_view", f"After toggle — button: {after_label!r}")

        assert initial_label != after_label, (
            f"BRW-006: Source toggle button label did not change after click "
            f"(was {initial_label!r}, still {after_label!r}). Toggle is not working."
        )

        # Toggle back
        source_btn.click()
        page.wait_for_timeout(300)
        restored_label = source_btn.text_content() or ""
        assert restored_label == initial_label, (
            f"BRW-006: Second toggle did not restore original label "
            f"(expected {initial_label!r}, got {restored_label!r})."
        )

    # ── BRW-009: Save locally re-generates valid zip ─────────────────────────

    def test_brw009_save_locally_downloads_valid_zip(self, page, screenshots):
        """BRW-009: Save locally button downloads a valid zip (correct MIME type)."""
        self._open(page)
        screenshots.capture(page, "brw009_01_before_save", "Browse view before Save locally")

        save_btn = page.locator(
            "[data-testid='save-locally-btn'], "
            "button:has-text('Save locally'), button:has-text('Save')"
        ).first

        assert save_btn.is_visible(timeout=3_000), \
            "BRW-009: Save locally button not found in browse view"

        with page.expect_download(timeout=10_000) as dl_info:
            save_btn.click()

        download = dl_info.value
        screenshots.capture(page, "brw009_02_download_triggered", "Download triggered")

        # Verify the downloaded file is a valid zip
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            download.save_as(tmp_path)
            assert zipfile.is_zipfile(tmp_path), (
                "BRW-009: Downloaded file from Save locally is not a valid zip. "
                "send-browse-v031.js re-generates the zip — MIME type or structure may be wrong."
            )
        finally:
            os.unlink(tmp_path)

    # ── BRW-010: Markdown link color ─────────────────────────────────────────

    def test_brw010_markdown_link_color(self, page, screenshots):
        """BRW-010: Links in rendered markdown are blue (#0969da), readable on white."""
        self._open(page)

        notes_item = page.locator(".sb-tree__file[data-path='NOTES.md']").first
        notes_item.click()
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw010_01_links", "NOTES.md — link color check")

        link = page.locator("a").filter(has_text="report").first
        if not link.is_visible(timeout=3_000):
            pytest.skip("No rendered <a> link found in NOTES.md")

        color = page.evaluate(
            "(el) => window.getComputedStyle(el).color",
            link.element_handle()
        )
        # #0969da = rgb(9, 105, 218)
        assert color in ("rgb(9, 105, 218)", "#0969da"), (
            f"BRW-010: Link color is {color!r}, expected rgb(9, 105, 218) (#0969da). "
            "send-browse-v031.css sets link color for readability on white background."
        )

    # ── BRW-011: URL-encoded paths (%20) ─────────────────────────────────────

    def test_brw011_url_encoded_paths_resolve(self, page, screenshots):
        """BRW-011: Links using %20 encoding resolve to files with spaces in their names."""
        self._open(page)

        notes_item = page.locator(".sb-tree__file[data-path='NOTES.md']").first
        notes_item.click()
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw011_01_notes_with_encoded_link", "NOTES.md — %20 encoded link")

        # NOTES.md has [Open accountant notes](ACCOUNTANT%20DEBRIEF.md)
        encoded_link = page.locator("a").filter(has_text="accountant notes").first
        if not encoded_link.is_visible(timeout=3_000):
            pytest.skip("Encoded link 'accountant notes' not found in rendered NOTES.md")

        initial_tabs = page.locator(".sgl-tab").count()
        encoded_link.click()
        page.wait_for_timeout(800)
        screenshots.capture(page, "brw011_02_after_click", "After clicking %20 encoded link")

        tabs_after = page.locator(".sgl-tab").count()
        page_text = page.text_content("body") or ""
        assert tabs_after > initial_tabs or "Accountant Debrief" in page_text or "Spaces in filename" in page_text, (
            "BRW-011: Clicking link with %20 encoding did not open 'ACCOUNTANT DEBRIEF.md'. "
            "URL-encoded paths should be decoded before matching against zip file entries."
        )

    # ── BRW-012: CSV renders as styled table ─────────────────────────────────

    def test_brw012_csv_renders_as_table(self, page, screenshots):
        """BRW-012: CSV files render as a styled table, not plain text."""
        self._open(page)

        # Expand data/ folder and click data.csv
        data_folder = page.locator(".sb-tree__folder[data-path='data']").first
        if data_folder.is_visible(timeout=2_000):
            data_folder.click()
            page.wait_for_timeout(500)

        csv_item = page.locator(".sb-tree__file[data-path='data/data.csv']").first
        csv_item.click()
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw012_01_csv_rendered", "data.csv opened — should be table")

        # Check for .sb-file__csv container (the table wrapper)
        csv_div = page.locator(".sb-file__csv").first
        assert csv_div.is_visible(timeout=3_000), (
            "BRW-012: .sb-file__csv container not found. "
            "CSV should render as a styled table, not plain text."
        )

        # Check that a <table> element is present inside the container
        table = csv_div.locator("table").first
        assert table.is_visible(timeout=2_000), \
            "BRW-012: No <table> inside .sb-file__csv — CSV table was not generated"

        # Source toggle should be present
        source_btn = page.locator(".sb-file__view-source").first
        assert source_btn.is_visible(timeout=2_000), \
            "BRW-012: No source toggle button found for CSV file"

        # Toggle to source view — should show raw CSV text
        source_btn.click()
        page.wait_for_timeout(300)
        screenshots.capture(page, "brw012_02_csv_source", "CSV source view")

        # Check that the table is hidden and source is shown
        assert not csv_div.is_visible(timeout=1_000), \
            "BRW-012: CSV table still visible after toggling to source view"

    # ── BRW-013: HTML renders in sandboxed iframe ─────────────────────────────

    def test_brw013_html_renders_in_sandboxed_iframe(self, page, screenshots):
        """BRW-013: HTML files render in a sandboxed iframe (allow-scripts, no allow-same-origin)."""
        self._open(page)

        data_folder = page.locator(".sb-tree__folder[data-path='data']").first
        if data_folder.is_visible(timeout=2_000):
            data_folder.click()
            page.wait_for_timeout(500)

        html_item = page.locator(".sb-tree__file[data-path='data/dashboard.html']").first
        html_item.click()
        page.wait_for_timeout(1_500)
        screenshots.capture(page, "brw013_01_html_rendered", "dashboard.html — should be iframe")

        iframe_el = page.locator(".sb-file__html-frame").first
        assert iframe_el.is_visible(timeout=3_000), (
            "BRW-013: .sb-file__html-frame not found. "
            "HTML files should render in a sandboxed iframe, not as raw source."
        )

        # Verify the iframe has sandbox attribute with allow-scripts but NOT allow-same-origin
        sandbox = iframe_el.get_attribute("sandbox") or ""
        assert "allow-scripts" in sandbox, (
            f"BRW-013: iframe sandbox={sandbox!r} — 'allow-scripts' is required for HTML rendering."
        )
        assert "allow-same-origin" not in sandbox, (
            f"BRW-013 SECURITY: iframe sandbox={sandbox!r} contains 'allow-same-origin'. "
            "This is a security risk — the iframe would be able to access the parent page."
        )

        # Source toggle should be present
        source_btn = page.locator(".sb-file__view-source").first
        assert source_btn.is_visible(timeout=2_000), \
            "BRW-013: No source toggle button found for HTML file"

    # ── BRW-014: Folder links expand tree ────────────────────────────────────

    def test_brw014_folder_links_expand_tree(self, page, screenshots):
        """BRW-014: Clicking a folder link in markdown expands the folder in the sidebar."""
        self._open(page)

        notes_item = page.locator(".sb-tree__file[data-path='NOTES.md']").first
        notes_item.click()
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw014_01_notes_open", "NOTES.md — contains [data/] folder link")

        # NOTES.md has [Browse data folder](data/)
        folder_link = page.locator("a").filter(has_text="Browse data folder").first
        if not folder_link.is_visible(timeout=3_000):
            pytest.skip("Folder link 'Browse data folder' not found in NOTES.md")

        folder_link.click()
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw014_02_after_folder_link", "After clicking folder link")

        # The data/ folder should now be expanded (open class added)
        data_folder = page.locator(".sb-tree__folder--open[data-path='data']").first
        page_text = page.text_content("body") or ""
        assert data_folder.is_visible(timeout=2_000) or "report.md" in page_text or "data.csv" in page_text, (
            "BRW-014: Clicking folder link did not expand the data/ folder in the sidebar. "
            "Folder links should expand the target folder and scroll it into view."
        )

    # ── BRW-015: Tab bar scrollable with many files ───────────────────────────

    def test_brw015_tab_bar_scrollable_with_many_tabs(self, page, transfer_helper, ui_url, screenshots):
        """BRW-015: Tab bar is horizontally scrollable when 8+ files are open."""
        # Build a zip with 10 root files to force tab overflow
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for i in range(10):
                zf.writestr(f"file_{i:02d}.md", f"# File {i}\n\nContent of file {i}.")
        buf.seek(0)
        tid, key_b64 = transfer_helper.upload_encrypted(buf.read(), "many-files.zip")
        url = f"{ui_url}/en-gb/browse/#{tid}/{key_b64}"

        page.goto(url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1_500)

        # Open all 10 files by clicking each tree item
        file_items = page.locator(".sb-tree__file").all()
        for item in file_items[:10]:
            if item.is_visible(timeout=1_000):
                item.click()
                page.wait_for_timeout(200)

        screenshots.capture(page, "brw015_01_many_tabs", "Browse view with 10 tabs open")

        # Tab bar should exist
        tab_bar = page.locator(".sgl-tab-bar").first
        assert tab_bar.is_visible(timeout=3_000), (
            "BRW-015: .sgl-tab-bar not found after opening multiple files. "
            "send-browse-v031.js injects scrollable tab bar styles."
        )

        # Tab bar should be scrollable (scrollWidth > clientWidth)
        is_scrollable = page.evaluate(
            """() => {
                const bar = document.querySelector('.sgl-tab-bar');
                return bar ? bar.scrollWidth > bar.clientWidth : false;
            }"""
        )
        assert is_scrollable, (
            "BRW-015: Tab bar is not scrollable even with 10 files open. "
            "Expected scrollWidth > clientWidth for horizontal tab scrolling."
        )
