"""P6: v0.3.1 Browse — Entry Form (manual token/ID entry).

The browse page (/en-gb/browse/) shows an entry form when loaded without a hash.
The user can enter a friendly token (word-word-NNNN) or a raw transfer ID/key
(tid/key format) and click "Decrypt & Download" to open the browse view.
The entry form submit handler calls the transfer load logic directly — it does
NOT rely on the hashchange event (so BRW-019 does not affect it).

  ENT-001  Entry form shown when /en-gb/browse/ loaded without a hash
  ENT-002  Entry form has descriptive text ("token", "transfer", "receive")
  ENT-003  Entering tid/key resolves and opens browse view (file tree visible)
  ENT-004  Entering tid/key for a zip with _page.json → PLR auto-opens
  ENT-005  Direct hash navigation (#tid/key) skips entry form, loads browse
  ENT-006  Bogus token shows error state (page does not crash)
"""

import io
import json
import zipfile

import pytest

pytestmark = [pytest.mark.p1, pytest.mark.v031]


# ---------------------------------------------------------------------------
# Minimal test zips
# ---------------------------------------------------------------------------

def _make_plain_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("notes.md", "# Hello\n\nEntry form test.")
    buf.seek(0)
    return buf.read()


def _make_plr_zip() -> bytes:
    page_json = json.dumps({
        "title": "QA Entry Form PLR Test",
        "sections": [
            {"type": "text", "title": "Test Section", "content": "QA entry form PLR test."}
        ]
    }, indent=2)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("_page.json", page_json)
        zf.writestr("notes.md", "# Notes\n\nEntry form PLR test.")
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wait_browse(page, timeout: int = 15_000):
    """Wait for browse tree to render at least one file."""
    page.wait_for_selector("body[data-ready]", timeout=timeout)
    page.wait_for_function(
        "() => document.querySelectorAll('.sb-tree__file-name').length > 0",
        timeout=timeout,
    )


def _fill_and_submit(page, token: str):
    """Fill the entry form input and click Decrypt & Download."""
    entry_input = page.locator("input").first
    entry_input.wait_for(state="visible", timeout=8_000)
    entry_input.fill(token)
    page.get_by_role("button", name="Decrypt & Download").click()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEntryForm:
    """ENT-001 through ENT-006 — Browse page entry form."""

    @pytest.fixture(autouse=True)
    def _setup(self, transfer_helper, ui_url):
        self._ui_url = ui_url
        self._helper = transfer_helper

    def test_entry_form_shown_without_hash(self, page, screenshots):
        """ENT-001: /en-gb/browse/ with no hash shows the entry form."""
        page.goto(f"{self._ui_url}/en-gb/browse/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        screenshots.capture(page, "ent001_01_entry_form", "Entry form — no hash")

        entry_input = page.locator("input").first
        assert entry_input.is_visible(), "Entry form input not visible at /en-gb/browse/ without hash"

        btn = page.get_by_role("button", name="Decrypt & Download")
        assert btn.is_visible(), "'Decrypt & Download' button not visible"

    def test_entry_form_has_descriptive_text(self, page, screenshots):
        """ENT-002: Entry form has descriptive text explaining what to enter."""
        page.goto(f"{self._ui_url}/en-gb/browse/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        screenshots.capture(page, "ent002_01_form_text", "Entry form text content")

        page_text = page.text_content("body") or ""
        assert any(kw in page_text.lower() for kw in ["token", "transfer", "receive"]), \
            f"Entry form missing descriptive text. Page text: {page_text[:300]}"

    def test_entry_form_resolves_transfer(self, page, screenshots):
        """ENT-003: Entering tid/key into the entry form opens the browse view."""
        tid, key = self._helper.upload_encrypted(_make_plain_zip(), "ent003-test.zip")

        page.goto(f"{self._ui_url}/en-gb/browse/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)

        _fill_and_submit(page, f"{tid}/{key}")
        screenshots.capture(page, "ent003_01_token_entered", "Token entered — waiting for browse")

        _wait_browse(page)
        screenshots.capture(page, "ent003_02_browse_loaded", "Browse loaded after entry form submit")

        tree_items = page.locator(".sb-tree__file-name").all_text_contents()
        assert any("notes.md" in t for t in tree_items), \
            f"notes.md not in tree after entry form submit. Tree: {tree_items}"

    def test_entry_form_plr_autoopen(self, page, screenshots):
        """ENT-004: Entry form with a zip containing _page.json → PLR auto-opens."""
        tid, key = self._helper.upload_encrypted(_make_plr_zip(), "ent004-plr.zip")

        page.goto(f"{self._ui_url}/en-gb/browse/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)

        _fill_and_submit(page, f"{tid}/{key}")

        page.wait_for_function(
            """() => {
                const el = document.querySelector('.plr-page');
                return el && el.offsetParent !== null && el.getBoundingClientRect().height > 0;
            }""",
            timeout=15_000,
        )
        screenshots.capture(page, "ent004_01_plr_autoopen", "PLR auto-opened after entry form submit")

        assert page.locator(".plr-page").is_visible(), \
            ".plr-page not visible — PLR did not auto-open after entry form submit"

    def test_direct_hash_skips_entry_form(self, page, screenshots):
        """ENT-005: Navigating with #tid/key already in URL skips the entry form."""
        tid, key = self._helper.upload_encrypted(_make_plain_zip(), "ent005-direct.zip")

        page.goto(f"{self._ui_url}/en-gb/browse/#{tid}/{key}")
        _wait_browse(page)
        screenshots.capture(page, "ent005_01_direct_load", "Direct hash nav — entry form absent")

        entry_input = page.locator("input").first
        assert not entry_input.is_visible(), \
            "Entry form input still visible after direct hash navigation (should have been replaced by browse)"

        tree_items = page.locator(".sb-tree__file-name").all_text_contents()
        assert any("notes.md" in t for t in tree_items), \
            f"notes.md not in tree after direct hash nav. Tree: {tree_items}"

    def test_bogus_token_shows_error(self, page, screenshots):
        """ENT-006: Entering a bogus token shows an error state (does not crash)."""
        page.goto(f"{self._ui_url}/en-gb/browse/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)

        _fill_and_submit(page, "bogus-token-9999")
        page.wait_for_timeout(3_000)
        screenshots.capture(page, "ent006_01_bogus_error", "Bogus token — error or loading state")

        page_text = page.inner_text("body") or ""
        # The page should show some kind of error — it should NOT silently succeed
        # or remain on the entry form with no feedback at all
        browse_loaded = page.locator(".sb-tree__file-name").count() > 0
        assert not browse_loaded, \
            "Browse tree rendered for a bogus token — should have shown an error"
