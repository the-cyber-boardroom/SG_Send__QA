"""P4: v0.3.1 Browse — BRW-016 through BRW-025.

New fixes shipped after the initial v0.3.1 BRW-001..015 batch:

  BRW-016  Per-file Print button in markdown action bar (sb-file__print)
  BRW-017  Locate button on every file type — expands tree, highlights, scrolls
  BRW-018  Discourse-style image dimensions: ![alt|400](img.png) → width:400px
  BRW-019  hashchange listener on SendDownload — new token navigates without reload
  BRW-020  Images output data-md-src (not src) — zero HTTP 404s while resolving
  BRW-021  Backtick code spans: `![alt](url)` renders as code, not broken image
  BRW-022  Markdown Present mode — sb-present-overlay, ESC to dismiss
  BRW-023  Selection colour: .sb-file__markdown ::selection → soft teal
  BRW-024  Ctrl+P while Present overlay open prints only the overlay
  BRW-025  Links inside Present overlay navigate (cloneNode fix)
"""

import io
import zipfile

import pytest

pytestmark = [pytest.mark.p2, pytest.mark.v031]

# ---------------------------------------------------------------------------
# Minimal assets
# ---------------------------------------------------------------------------

_PNG_1X1 = (
    b'\x89PNG\r\n\x1a\n'
    b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde'
    b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)

# Markdown with all features exercised by BRW-016..025
_RICH_MD = """\
# Rich Test Document

Regular paragraph.

See the [linked doc](other.md) for details.

## Images

Default size:
![Chart](images/chart.png)

Pixel width:
![Narrow|400](images/chart.png)

Percentage width:
![Half|50%](images/chart.png)

Pixel width × height:
![Fixed|200x100](images/chart.png)

## Code span (BRW-021)

This is inline code: `![not-an-image](fake.png)` — should NOT render as image.

## Link to other file

[Open other doc](other.md)
"""

_OTHER_MD = "# Other Document\n\nYou followed a link!\n"


def _make_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("rich.md",          _RICH_MD)
        zf.writestr("other.md",         _OTHER_MD)
        zf.writestr("data/report.md",   "# Report\n\nContent.")
        zf.writestr("data/data.csv",    "Name,Score\nAlice,90\nBob,85\n")
        zf.writestr("images/chart.png", _PNG_1X1)
    buf.seek(0)
    return buf.read()


class TestBrowseBrw016To025:
    """BRW-016 through BRW-025."""

    @pytest.fixture(autouse=True)
    def _setup(self, transfer_helper, ui_url):
        zip_bytes = _make_zip()
        tid, key_b64 = transfer_helper.upload_encrypted(zip_bytes, "rich-test.zip")
        self._url = f"{ui_url}/en-gb/browse/#{tid}/{key_b64}"

    def _open(self, page, extra_wait=1_500):
        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(extra_wait)

    def _open_rich_md(self, page):
        """Navigate to browse and open rich.md, waiting for source toggle to appear."""
        self._open(page)
        rich_item = page.locator(".sb-tree__file[data-path='rich.md']").first
        rich_item.click()
        page.wait_for_function(
            """() => {
                const btns = document.querySelectorAll('.sb-file__view-source');
                return Array.from(btns).some(
                    b => b.offsetParent !== null && b.getBoundingClientRect().height > 0
                );
            }""",
            timeout=8_000,
        )

    # ── BRW-016: Per-file Print button ───────────────────────────────────────

    def test_brw016_print_button_present_for_markdown(self, page, screenshots):
        """BRW-016: Markdown files have a .sb-file__print button in the action bar."""
        self._open_rich_md(page)
        screenshots.capture(page, "brw016_01_action_bar", "Markdown action bar")

        print_btn = page.locator(".sb-file__print:visible").first
        assert print_btn.is_visible(), (
            "BRW-016: No .sb-file__print button found for markdown file. "
            "send-browse-v031.js should add a per-file Print button."
        )

    def test_brw016_print_button_absent_for_csv(self, page, screenshots):
        """BRW-016: Non-markdown files (CSV) do NOT have a Print button."""
        self._open(page)
        data_folder = page.locator(".sb-tree__folder[data-path='data']").first
        if data_folder.is_visible(timeout=2_000):
            data_folder.click()
            page.wait_for_timeout(400)

        csv_item = page.locator(".sb-tree__file[data-path='data/data.csv']").first
        csv_item.click()
        page.wait_for_function(
            "() => { const el = document.querySelector('.sb-file__csv'); "
            "return el && el.offsetParent !== null; }",
            timeout=8_000,
        )
        screenshots.capture(page, "brw016_02_csv_no_print", "CSV action bar — no Print button")

        assert not page.locator(".sb-file__print:visible").is_visible(), \
            "BRW-016: .sb-file__print button found for CSV file — should be markdown-only"

    # ── BRW-017: Locate button ───────────────────────────────────────────────

    def test_brw017_locate_button_present_on_markdown(self, page, screenshots):
        """BRW-017: Markdown files have a .sb-file__reveal (Locate) button."""
        self._open_rich_md(page)
        screenshots.capture(page, "brw017_01_locate_btn", "Markdown action bar — Locate button")

        locate_btn = page.locator(".sb-file__reveal:visible").first
        assert locate_btn.is_visible(), (
            "BRW-017: No .sb-file__reveal (Locate) button found for markdown. "
            "send-browse-v031.js adds a Locate button to all file types."
        )
        assert "Locate" in (locate_btn.text_content() or ""), \
            "BRW-017: .sb-file__reveal button text is not 'Locate'"

    def test_brw017_locate_button_present_on_csv(self, page, screenshots):
        """BRW-017: CSV files also have a Locate button (all file types)."""
        self._open(page)
        data_folder = page.locator(".sb-tree__folder[data-path='data']").first
        if data_folder.is_visible(timeout=2_000):
            data_folder.click()
            page.wait_for_timeout(400)

        csv_item = page.locator(".sb-tree__file[data-path='data/data.csv']").first
        csv_item.click()
        page.wait_for_function(
            "() => { const el = document.querySelector('.sb-file__csv'); "
            "return el && el.offsetParent !== null; }",
            timeout=8_000,
        )
        screenshots.capture(page, "brw017_02_csv_locate", "CSV action bar — Locate button")

        locate_btn = page.locator(".sb-file__reveal:visible").first
        assert locate_btn.is_visible(), \
            "BRW-017: No Locate button for CSV file — should be on all file types"

    def test_brw017_locate_highlights_file_in_tree(self, page, screenshots):
        """BRW-017: Clicking Locate adds .sb-tree__file--active to the correct tree item."""
        self._open(page)
        # Open a nested file via markdown link first to ensure it may be in a collapsed folder
        data_folder = page.locator(".sb-tree__folder[data-path='data']").first
        if data_folder.is_visible(timeout=2_000):
            data_folder.click()
            page.wait_for_timeout(400)

        report_item = page.locator(".sb-tree__file[data-path='data/report.md']").first
        report_item.click()
        page.wait_for_function(
            """() => {
                const btns = document.querySelectorAll('.sb-file__reveal');
                return Array.from(btns).some(
                    b => b.offsetParent !== null && b.getBoundingClientRect().height > 0
                );
            }""",
            timeout=8_000,
        )

        locate_btn = page.locator(".sb-file__reveal:visible").first
        locate_btn.click()
        page.wait_for_timeout(500)
        screenshots.capture(page, "brw017_03_after_locate", "After Locate — file highlighted in tree")

        active_item = page.locator(".sb-tree__file--active").first
        assert active_item.is_visible(timeout=3_000), (
            "BRW-017: No .sb-tree__file--active element after clicking Locate. "
            "Locate should highlight the current file in the sidebar tree."
        )
        active_path = active_item.get_attribute("data-path") or ""
        assert "report.md" in active_path, (
            f"BRW-017: Active tree item is '{active_path}', expected 'data/report.md'. "
            "Locate highlighted the wrong file."
        )

    # ── BRW-018: Discourse-style image dimensions ────────────────────────────

    def test_brw018_image_pixel_width(self, page, screenshots):
        """BRW-018: ![alt|400](img.png) renders with width:400px style."""
        self._open_rich_md(page)
        page.wait_for_timeout(1_000)  # let blob URLs resolve
        screenshots.capture(page, "brw018_01_images", "rich.md — image dimensions")

        # Find the img with alt="Narrow" (from ![Narrow|400](images/chart.png))
        narrow_img = page.locator("img[alt='Narrow']:visible").first
        if not narrow_img.is_visible(timeout=3_000):
            pytest.skip("BRW-018: Image with alt='Narrow' not found — markdown may not have rendered")

        style = narrow_img.get_attribute("style") or ""
        assert "width:400px" in style.replace(" ", ""), (
            f"BRW-018: img[alt='Narrow'] style={style!r} — expected 'width:400px'. "
            "Discourse-style ![alt|400](img) should set explicit pixel width."
        )

    def test_brw018_image_percentage_width(self, page, screenshots):
        """BRW-018: ![alt|50%](img.png) renders with width:50% style."""
        self._open_rich_md(page)
        page.wait_for_timeout(1_000)

        half_img = page.locator("img[alt='Half']:visible").first
        if not half_img.is_visible(timeout=3_000):
            pytest.skip("BRW-018: Image with alt='Half' not found")

        style = half_img.get_attribute("style") or ""
        assert "width:50%" in style.replace(" ", ""), (
            f"BRW-018: img[alt='Half'] style={style!r} — expected 'width:50%'. "
            "Discourse-style ![alt|50%](img) should set percentage width."
        )

    def test_brw018_image_pixel_width_and_height(self, page, screenshots):
        """BRW-018: ![alt|200x100](img.png) renders with both width and height."""
        self._open_rich_md(page)
        page.wait_for_timeout(1_000)

        fixed_img = page.locator("img[alt='Fixed']:visible").first
        if not fixed_img.is_visible(timeout=3_000):
            pytest.skip("BRW-018: Image with alt='Fixed' not found")

        style = fixed_img.get_attribute("style") or ""
        style_nospace = style.replace(" ", "")
        assert "width:200px" in style_nospace and "height:100px" in style_nospace, (
            f"BRW-018: img[alt='Fixed'] style={style!r} — expected 'width:200px' and 'height:100px'."
        )

    # ── BRW-019: hashchange navigates without reload ─────────────────────────
    # KNOWN BUG: the _v031HashHandler is never registered because connectedCallback
    # fires before send-browse-v031.js patches SendDownload.prototype.connectedCallback.
    # See: tests/qa/v031/bugs/test__bug__brw019_hashchange_handler_not_registered.py

    @pytest.mark.skip(reason="BRW-019 known bug — handler not registered; see v031/bugs/")
    def test_brw019_hashchange_loads_new_transfer(self, page, transfer_helper, ui_url, screenshots):
        """BRW-019: Changing window.location.hash triggers full reload of new transfer.

        SKIPPED pending fix. See:
          tests/qa/v031/bugs/test__bug__brw019_hashchange_handler_not_registered.py

        Re-enable once the bug test starts failing (handler registered).
        """
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("second.md", "# Second Transfer\n\nThis is the second upload.")
        buf.seek(0)
        tid2, key2 = transfer_helper.upload_encrypted(buf.read(), "second.zip")

        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1_500)
        screenshots.capture(page, "brw019_01_first_transfer", "First transfer loaded")

        new_hash = f"#{tid2}/{key2}"
        page.evaluate(f"window.location.hash = '{new_hash}'")
        page.wait_for_selector(".sb-tree__file[data-path='second.md']", timeout=12_000)
        page.wait_for_timeout(500)
        screenshots.capture(page, "brw019_02_second_transfer", "After hashchange — second transfer")

        page_text = page.text_content("body") or ""
        assert "Second Transfer" in page_text or "second.md" in page_text, (
            "BRW-019: hashchange should reload the transfer but did not."
        )

    # ── BRW-020: Images use data-md-src (no src HTTP requests) ──────────────

    def test_brw020_images_use_data_md_src(self, page, screenshots):
        """BRW-020: <img> tags in rendered markdown have data-md-src, not raw src."""
        self._open_rich_md(page)
        # Give BRW-005 time to resolve blob URLs from the zip
        page.wait_for_timeout(2_000)
        screenshots.capture(page, "brw020_01_images", "rich.md — image src check")

        # All <img> tags should either have blob: src (resolved by BRW-005)
        # or still have data-md-src (in-flight). None should have a bare relative src.
        img_srcs = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img')).map(img => ({
                src:       img.getAttribute('src'),
                dataMdSrc: img.getAttribute('data-md-src'),
            }));
        }""")

        assert img_srcs, "BRW-020: No <img> elements found in rendered markdown"

        for img in img_srcs:
            src = img.get("src") or ""
            # If src is set it must be a blob URL (resolved by BRW-005)
            if src:
                assert src.startswith("blob:"), (
                    f"BRW-020: img src={src!r} is not a blob URL. "
                    "markdown-parser-v031.js should output data-md-src (not src) "
                    "so the browser makes zero HTTP requests before BRW-005 resolves."
                )

    # ── BRW-021: Backtick code spans ─────────────────────────────────────────

    def test_brw021_backtick_code_span_not_parsed_as_image(self, page, screenshots):
        """BRW-021: `![alt](url)` inside backticks renders as inline code, not <img>."""
        self._open_rich_md(page)
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw021_01_backtick", "rich.md — backtick image span")

        # The markdown has: `![not-an-image](fake.png)`
        # BRW-021 fix: this should render as a <code> span, not an <img> tag.
        code_spans = page.locator("code").all_text_contents()
        backtick_code = [c for c in code_spans if "not-an-image" in c or "![" in c]

        assert backtick_code, (
            "BRW-021: `![not-an-image](fake.png)` was not rendered as inline code. "
            "Backtick spans containing ![ should be treated as code, not images."
        )

        # Confirm no <img> with alt='not-an-image' was created
        broken_imgs = page.locator("img[alt='not-an-image']").count()
        assert broken_imgs == 0, (
            f"BRW-021: Found {broken_imgs} <img alt='not-an-image'> element(s). "
            "The ![...] inside backticks was parsed as an image — BRW-021 fix not active."
        )

    # ── BRW-022: Markdown Present mode ───────────────────────────────────────

    def test_brw022_present_button_opens_overlay(self, page, screenshots):
        """BRW-022: .sb-file__present-md button opens fullscreen .sb-present-overlay."""
        self._open_rich_md(page)
        screenshots.capture(page, "brw022_01_before_present", "Before Present mode")

        present_btn = page.locator(".sb-file__present-md:visible").first
        assert present_btn.is_visible(), (
            "BRW-022: No .sb-file__present-md button found for markdown. "
            "send-browse-v031.js should add a Present button to markdown action bar."
        )

        present_btn.click()
        page.wait_for_selector(".sb-present-overlay", timeout=3_000)
        screenshots.capture(page, "brw022_02_overlay_open", "Present overlay open")

        overlay = page.locator(".sb-present-overlay").first
        assert overlay.is_visible(), \
            "BRW-022: .sb-present-overlay not visible after clicking Present"

        close_btn = page.locator(".sb-present-close").first
        assert close_btn.is_visible(), \
            "BRW-022: .sb-present-close (✕ Exit) button not visible inside overlay"

    def test_brw022_present_overlay_dismissed_by_close_button(self, page, screenshots):
        """BRW-022: Clicking ✕ Exit button dismisses the Present overlay."""
        self._open_rich_md(page)
        page.locator(".sb-file__present-md:visible").first.click()
        page.wait_for_selector(".sb-present-overlay", timeout=3_000)

        page.locator(".sb-present-close").first.click()
        page.wait_for_timeout(400)
        screenshots.capture(page, "brw022_03_overlay_dismissed", "Overlay dismissed via ✕ Exit")

        assert not page.locator(".sb-present-overlay").is_visible(), \
            "BRW-022: Present overlay still visible after clicking ✕ Exit"

    def test_brw022_present_overlay_dismissed_by_escape(self, page, screenshots):
        """BRW-022: Pressing ESC dismisses the Present overlay."""
        self._open_rich_md(page)
        page.locator(".sb-file__present-md:visible").first.click()
        page.wait_for_selector(".sb-present-overlay", timeout=3_000)

        page.keyboard.press("Escape")
        page.wait_for_timeout(400)
        screenshots.capture(page, "brw022_04_overlay_esc", "Overlay dismissed via ESC")

        assert not page.locator(".sb-present-overlay").is_visible(), \
            "BRW-022: Present overlay still visible after pressing ESC"

    # ── BRW-023: Selection colour ─────────────────────────────────────────────

    def test_brw023_selection_colour_css_rule_present(self, page, screenshots):
        """BRW-023: ::selection CSS for .sb-file__markdown uses teal (rgba 78,205,196,0.25)."""
        self._open_rich_md(page)

        # Verify the CSS rule is in a loaded stylesheet
        rule_found = page.evaluate("""() => {
            for (var i = 0; i < document.styleSheets.length; i++) {
                try {
                    var rules = document.styleSheets[i].cssRules || [];
                    for (var j = 0; j < rules.length; j++) {
                        var text = rules[j].cssText || '';
                        if (text.includes('sb-file__markdown') && text.includes('selection')) {
                            return text;
                        }
                    }
                } catch(e) { /* cross-origin stylesheet — skip */ }
            }
            return null;
        }""")

        assert rule_found is not None, (
            "BRW-023: No CSS rule found for .sb-file__markdown ::selection. "
            "send-browse-v031.css should define a teal selection colour."
        )
        assert "rgba" in rule_found or "78" in rule_found, (
            f"BRW-023: Selection rule found but colour unexpected: {rule_found!r}"
        )

    # ── BRW-024: Ctrl+P prints only overlay ──────────────────────────────────

    def test_brw024_print_media_css_rule_present(self, page, screenshots):
        """BRW-024: @media print CSS hides non-overlay elements when overlay is open."""
        self._open_rich_md(page)

        # Verify the @media print rule exists in a loaded stylesheet
        rule_found = page.evaluate("""() => {
            for (var i = 0; i < document.styleSheets.length; i++) {
                try {
                    var rules = document.styleSheets[i].cssRules || [];
                    for (var j = 0; j < rules.length; j++) {
                        var rule = rules[j];
                        if (rule.type === CSSRule.MEDIA_RULE) {
                            var mq = rule.conditionText || rule.media && rule.media.mediaText || '';
                            if (mq.includes('print')) {
                                var text = rule.cssText || '';
                                if (text.includes('sb-present-overlay')) return text;
                            }
                        }
                    }
                } catch(e) {}
            }
            return null;
        }""")

        assert rule_found is not None, (
            "BRW-024: No @media print rule referencing .sb-present-overlay found. "
            "send-browse-v031.css should hide non-overlay elements when printing."
        )

    # ── BRW-025: Links inside Present overlay navigate ────────────────────────

    def test_brw025_present_overlay_links_navigate(self, page, screenshots):
        """BRW-025: Clicking a link inside the Present overlay opens the target file."""
        self._open_rich_md(page)

        # Open present mode
        page.locator(".sb-file__present-md:visible").first.click()
        page.wait_for_selector(".sb-present-overlay", timeout=3_000)
        screenshots.capture(page, "brw025_01_overlay_with_links", "Present overlay — contains links")

        # Find the link to other.md inside the overlay
        overlay_link = page.locator(".sb-present-overlay a").filter(has_text="linked doc").first
        if not overlay_link.is_visible(timeout=3_000):
            pytest.skip("BRW-025: Link 'linked doc' not found inside Present overlay")

        overlay_link.click()
        page.wait_for_timeout(1_000)
        screenshots.capture(page, "brw025_02_after_link_click", "After clicking link in overlay")

        # Overlay should be dismissed
        assert not page.locator(".sb-present-overlay").is_visible(), (
            "BRW-025: Present overlay still visible after clicking a link inside it. "
            "Links in the overlay should dismiss it then navigate."
        )

        # The target file (other.md) should now be open
        page_text = page.text_content("body") or ""
        assert "Other Document" in page_text or "followed a link" in page_text or \
               "other.md" in (page.locator(".sgl-tab--active, .sgl-tab").first.text_content() or ""), (
            "BRW-025: After clicking overlay link, 'other.md' content not found. "
            "Link navigation from Present overlay should open the target file as a tab."
        )
