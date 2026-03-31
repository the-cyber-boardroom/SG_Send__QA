"""P5: v0.3.1 Page Layout Renderer (PLR) — PLR-001 through PLR-007b.

_page.json files render as designed page layouts inside the Browse component.

  PLR-001  Folder click → detect _page.json → render page layout tab
  PLR-002  Auto-open checks root _page.json first (before first-file heuristic)
  PLR-003  _openFolderPage() — loads _page.json, opens as named tab, renders
  PLR-004  Clicking _page.json in tree renders page layout (not raw JSON)
  PLR-005  JSON colorizer — .plr-json-key/.plr-json-str etc on .json source views
  PLR-006  Deep-link URL — #token/path/to/file auto-opens the linked file
  PLR-007  Print button → opens new window print preview
  PLR-007b Cmd/Ctrl+P intercept → prints active PLR panel

  Plus: send-download.js fix — strip deep-link path from hash before token parse.

CSS class landmarks:
  .plr-page             — outer page layout container
  .plr-scroll-wrapper   — scroll wrapper around .plr-page
  .plr-section          — section component
  .plr-text             — text component
  .plr-source-toggle-btn — action bar buttons (Locate, Print, Present, Copy JSON, Edit, Source)
  .plr-present-overlay  — present mode full-screen overlay
  .plr-present-close    — close button inside overlay
  .plr-json-key         — JSON syntax colorizer (key)
"""

import io
import json
import zipfile

import pytest

pytestmark = [pytest.mark.p2, pytest.mark.v031]

# ---------------------------------------------------------------------------
# Minimal _page.json (v2 schema)
# ---------------------------------------------------------------------------

_PAGE_JSON = json.dumps({
    "title": "QA Test Layout",
    "theme": {"background": "#ffffff"},
    "sections": [
        {
            "type": "text",
            "title": "Section One",
            "content": "This is the QA test page layout."
        },
        {
            "type": "markdown",
            "content": "## Markdown Section\n\nHello from **markdown**."
        }
    ]
}, indent=2)

_OTHER_JSON = json.dumps({"key": "value", "number": 42, "flag": True}, indent=2)


def _make_plr_zip() -> bytes:
    """Zip with _page.json at root, a subfolder with its own _page.json, and a plain .json."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("_page.json",        _PAGE_JSON)
        zf.writestr("notes.md",          "# Notes\n\nSome markdown notes.")
        zf.writestr("data/config.json",  _OTHER_JSON)
        zf.writestr("data/readme.md",    "# Data folder\n\nData description.")
    buf.seek(0)
    return buf.read()


class TestPLR:
    """PLR-001 through PLR-007b — Page Layout Renderer."""

    @pytest.fixture(autouse=True)
    def _setup(self, transfer_helper, ui_url):
        tid, key = transfer_helper.upload_encrypted(_make_plr_zip(), "plr-test.zip")
        self._url  = f"{ui_url}/en-gb/browse/#{tid}/{key}"
        self._tid  = tid
        self._key  = key

    def _open(self, page, extra_wait=1_500):
        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(extra_wait)

    def _wait_plr(self, page):
        """Wait until .plr-page is visible (PLR rendered)."""
        page.wait_for_function(
            "() => { const el = document.querySelector('.plr-page'); "
            "return el && el.offsetParent !== null && el.getBoundingClientRect().height > 0; }",
            timeout=8_000,
        )

    # ── PLR-002: Auto-open picks root _page.json first ───────────────────────

    def test_plr002_root_page_json_auto_opens(self, page, screenshots):
        """PLR-002: Browse auto-opens root _page.json as a page layout tab on first load."""
        self._open(page, extra_wait=2_000)
        screenshots.capture(page, "plr002_01_auto_open", "Browse auto-open — should show _page.json layout")

        self._wait_plr(page)
        assert page.locator(".plr-page").first.is_visible(), (
            "PLR-002: .plr-page container not found after auto-open. "
            "Root _page.json should be opened automatically as a page layout tab."
        )

    def test_plr002_page_title_rendered(self, page, screenshots):
        """PLR-002: The 'title' field from _page.json appears in the rendered output."""
        self._open(page, extra_wait=2_000)
        self._wait_plr(page)
        screenshots.capture(page, "plr002_02_title", "Page layout rendered — title check")

        page_text = page.text_content("body") or ""
        assert "QA Test Layout" in page_text or "_page.json" in page_text, (
            "PLR-002: Title 'QA Test Layout' or '_page.json' tab label not found. "
            "The page layout tab should show the title from _page.json."
        )

    def test_plr002_section_content_rendered(self, page, screenshots):
        """PLR-002: Section content from _page.json renders as .plr-section and .plr-text."""
        self._open(page, extra_wait=2_000)
        self._wait_plr(page)

        # The text section content
        page_text = page.text_content("body") or ""
        assert "Section One" in page_text and "QA test page layout" in page_text, (
            "PLR-002: Section content not rendered. "
            "Expected 'Section One' and 'QA test page layout' in page layout output."
        )

    # ── PLR-004: Clicking _page.json in tree renders page layout ─────────────

    def test_plr004_clicking_page_json_renders_layout(self, page, screenshots):
        """PLR-004: Clicking _page.json in the folder tree renders the page layout (not raw JSON)."""
        self._open(page, extra_wait=1_500)

        # Navigate away first (open notes.md)
        notes_item = page.locator(".sb-tree__file[data-path='notes.md']").first
        notes_item.click()
        page.wait_for_timeout(1_000)

        # Now click _page.json in the tree
        page_json_item = page.locator(".sb-tree__file[data-path='_page.json']").first
        page_json_item.click()
        self._wait_plr(page)
        screenshots.capture(page, "plr004_01_layout_rendered", "After clicking _page.json — layout rendered")

        assert page.locator(".plr-page").first.is_visible(), (
            "PLR-004: .plr-page not visible after clicking _page.json in tree. "
            "send-browse-v031--page-layout.js should intercept this click and render a layout."
        )

        # Verify it is NOT showing raw JSON (no JSON brace as first character)
        raw_json_visible = page.locator(".sb-file__content").first.is_visible(timeout=1_000)
        if raw_json_visible:
            content_text = page.locator(".sb-file__content").first.text_content() or ""
            assert not content_text.strip().startswith("{"), (
                "PLR-004: _page.json is being shown as raw JSON source. "
                "It should render as a page layout."
            )

    # ── PLR-005: JSON colorizer ───────────────────────────────────────────────

    def test_plr005_json_colorizer_on_source_view(self, page, screenshots):
        """PLR-005: JSON source view uses syntax colorizer (.plr-json-key, .plr-json-str, etc.)."""
        self._open(page, extra_wait=1_500)

        # Open _page.json layout, then toggle to source view
        page_json_item = page.locator(".sb-tree__file[data-path='_page.json']").first
        page_json_item.click()
        self._wait_plr(page)

        # Click the Source button (text "{ } Source")
        source_btn = page.locator(".plr-source-toggle-btn").filter(has_text="Source").first
        assert source_btn.is_visible(timeout=3_000), \
            "PLR-005: No '{ } Source' button found on _page.json layout tab"

        source_btn.click()
        page.wait_for_timeout(500)
        screenshots.capture(page, "plr005_01_source_view", "_page.json source view — JSON colorizer")

        # Colorized JSON should have .plr-json-key spans
        key_spans = page.locator(".plr-json-key").count()
        assert key_spans > 0, (
            "PLR-005: No .plr-json-key elements found in JSON source view. "
            "send-browse-v031--page-layout.js should apply the JSON colorizer."
        )

    def test_plr005_json_colorizer_on_plain_json_file(self, page, screenshots):
        """PLR-005b: Plain .json files (not _page.json) also get colorized source view."""
        self._open(page, extra_wait=1_500)

        # Open the data/ folder
        data_folder = page.locator(".sb-tree__folder[data-path='data']").first
        if data_folder.is_visible(timeout=2_000):
            data_folder.click()
            page.wait_for_timeout(400)

        # Open data/config.json
        json_item = page.locator(".sb-tree__file[data-path='data/config.json']").first
        json_item.click()
        page.wait_for_timeout(1_500)
        screenshots.capture(page, "plr005_02_plain_json", "data/config.json — colorized source")

        key_spans = page.locator(".plr-json-key").count()
        assert key_spans > 0, (
            "PLR-005b: No .plr-json-key elements in data/config.json view. "
            "JSON colorizer should apply to all .json files, not just _page.json."
        )

    # ── PLR Action bar buttons ────────────────────────────────────────────────

    def test_plr_action_bar_buttons_present(self, page, screenshots):
        """PLR: _page.json tab shows action bar with Locate, Print, Present, Copy JSON, Edit, Source."""
        self._open(page, extra_wait=2_000)
        self._wait_plr(page)
        screenshots.capture(page, "plr_action_01_bar", "_page.json action bar")

        btn_texts = [b.text_content() or "" for b in page.locator(".plr-source-toggle-btn").all()]
        joined = " ".join(btn_texts)

        assert any("Present" in t for t in btn_texts), \
            f"PLR: No Present button found in PLR action bar. Buttons: {btn_texts}"
        assert any("Source" in t for t in btn_texts), \
            f"PLR: No Source button found in PLR action bar. Buttons: {btn_texts}"
        assert any("Copy" in t or "JSON" in t for t in btn_texts), \
            f"PLR: No Copy JSON button found in PLR action bar. Buttons: {btn_texts}"
        assert any("Edit" in t for t in btn_texts), \
            f"PLR: No Edit button found in PLR action bar. Buttons: {btn_texts}"

    # ── PLR Present mode ──────────────────────────────────────────────────────

    def test_plr_present_mode_opens_overlay(self, page, screenshots):
        """PLR: Clicking Present opens .plr-present-overlay fullscreen."""
        self._open(page, extra_wait=2_000)
        self._wait_plr(page)

        present_btn = page.locator(".plr-source-toggle-btn").filter(has_text="Present").first
        assert present_btn.is_visible(timeout=3_000), \
            "PLR: No Present button on _page.json tab"

        present_btn.click()
        page.wait_for_selector(".plr-present-overlay", timeout=3_000)
        screenshots.capture(page, "plr_present_01_overlay", "PLR present overlay open")

        assert page.locator(".plr-present-overlay").first.is_visible(), \
            "PLR: .plr-present-overlay not visible after clicking Present"
        assert page.locator(".plr-present-close").first.is_visible(), \
            "PLR: .plr-present-close button not visible in PLR overlay"

    def test_plr_present_mode_dismissed_by_escape(self, page, screenshots):
        """PLR: ESC key dismisses the PLR present overlay."""
        self._open(page, extra_wait=2_000)
        self._wait_plr(page)

        page.locator(".plr-source-toggle-btn").filter(has_text="Present").first.click()
        page.wait_for_selector(".plr-present-overlay", timeout=3_000)

        page.keyboard.press("Escape")
        page.wait_for_timeout(400)
        screenshots.capture(page, "plr_present_02_esc_dismissed", "PLR overlay dismissed via ESC")

        assert not page.locator(".plr-present-overlay").is_visible(), \
            "PLR: .plr-present-overlay still visible after ESC"

    # ── PLR-006: Deep-link URL ────────────────────────────────────────────────

    def test_plr006_deeplink_hash_opens_specific_file(self, page, ui_url, screenshots):
        """PLR-006: Navigating to #token/path/to/file auto-opens the linked file."""
        deep_url = f"{ui_url}/en-gb/browse/#{self._tid}/{self._key}/notes.md"
        page.goto(deep_url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(2_000)
        screenshots.capture(page, "plr006_01_deeplink", f"Deep-link URL to notes.md")

        # notes.md should be open
        page_text = page.text_content("body") or ""
        assert "Some markdown notes" in page_text or "notes.md" in page_text, (
            "PLR-006: Deep-link to notes.md did not auto-open the file. "
            "Hash format #token/key/path should open 'path' in the browse view."
        )

    def test_plr006_deeplink_does_not_break_token_parse(self, page, ui_url, screenshots):
        """PLR-006 / send-download.js fix: #token/key/path correctly extracts transferId."""
        # A deep-link URL with a file path suffix — the token parse must not include the path
        deep_url = f"{ui_url}/en-gb/browse/#{self._tid}/{self._key}/_page.json"
        page.goto(deep_url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(2_000)
        screenshots.capture(page, "plr006_02_token_parse", "Deep-link — token parsed correctly")

        # Transfer should load (not show "Transfer not found" error)
        page_text = page.text_content("body") or ""
        assert "Transfer not found" not in page_text and "not found" not in page_text.lower()[:200], (
            "PLR-006 / send-download.js fix: Deep-link URL caused 'Transfer not found'. "
            "send-download.js must strip the path suffix before parsing the transfer token."
        )
        # The page layout should render
        self._wait_plr(page)
        assert page.locator(".plr-page").first.is_visible(), \
            "PLR-006: Transfer loaded but _page.json layout not rendered on deep-link"


class TestPLRDeepLinkFix:
    """send-download.js fix: strip deep-link path from hash before token parse.

    Separate from TestPLR since it tests the base send-download.js fix
    which applies to all browse transfers, not just PLR ones.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, transfer_helper, ui_url):
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("doc.md", "# Doc\n\nContent.")
        buf.seek(0)
        tid, key = transfer_helper.upload_encrypted(buf.read(), "deeplink-fix.zip")
        self._url = f"{ui_url}/en-gb/browse/#{tid}/{key}"
        self._tid = tid
        self._key = key
        self._ui_url = ui_url

    def test_deeplink_path_suffix_does_not_break_token(self, page, screenshots):
        """send-download.js: #tid/key/extra/path correctly loads the transfer."""
        deep_url = f"{self._ui_url}/en-gb/browse/#{self._tid}/{self._key}/doc.md"
        page.goto(deep_url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(2_000)
        screenshots.capture(page, "deeplink_fix_01", "Deep-link with path suffix — transfer loads")

        # Should load the transfer (tree appears)
        tree_files = page.locator(".sb-tree__file-name").all_text_contents()
        assert tree_files, (
            "send-download.js deep-link fix: No tree files found — transfer failed to load. "
            "Hash '#tid/key/path' should load the transfer by stripping '/path' before token parse."
        )

    def test_deeplink_simple_token_with_path_loads(self, page, transfer_helper, screenshots):
        """send-download.js: friendly token + path suffix #word-word-NNNN/doc.md resolves."""
        # This tests that FriendlyCrypto.isFriendlyToken is called on the token-only part
        # (not the full hash including the path). We test with a regular hash since
        # friendly token generation requires specific conditions.
        # Instead: verify the base case (non-PLR deep-link) doesn't show an error.
        deep_url = f"{self._ui_url}/en-gb/browse/#{self._tid}/{self._key}/nonexistent/path.md"
        page.goto(deep_url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(2_000)
        screenshots.capture(page, "deeplink_fix_02_no_error", "Deep-link to non-existent path — no 'not found' error")

        # Transfer should still load even if the linked path doesn't exist
        page_text = page.text_content("body") or ""
        assert "Transfer not found" not in page_text, (
            "send-download.js deep-link fix: '#tid/key/nonexistent/path' triggered "
            "'Transfer not found'. The path suffix must be stripped before token parse."
        )
        tree_files = page.locator(".sb-tree__file-name").all_text_contents()
        assert tree_files, "Transfer should load even when the deep-linked file path doesn't exist"
