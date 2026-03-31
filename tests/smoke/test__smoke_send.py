"""Smoke tests for SG/Send live environments (dev / main / prod).

Runs a core health-check against the configured target environment.
Split into two classes:

  SmokeNoAuth   — navigation-only, no upload credentials required.
                  Always run. Catches deploy failures, UI regressions,
                  JS errors, and structural changes immediately.

  SmokeUpload   — full round-trip: upload → browse → verify.
                  Requires SG_SEND_ACCESS_TOKEN (or --access-token).
                  Catches crypto/SGMETA regressions, browse rendering
                  failures, and PLR issues against the live environment.

Run against dev (default):
    pytest tests/smoke/ -v

Run against pre-prod with uploads:
    pytest tests/smoke/ -v --target=main --access-token=<token>
"""

import io
import json
import zipfile

import pytest


# ── Shared helpers ────────────────────────────────────────────────────────────

def _wait_browse(page, timeout: int = 20_000):
    """Wait for browse tree to render at least one file."""
    page.wait_for_selector("body[data-ready]", timeout=timeout)
    page.wait_for_function(
        "() => document.querySelectorAll('.sb-tree__file-name').length > 0",
        timeout=timeout,
    )


def _wait_plr(page, timeout: int = 20_000):
    """Wait until .plr-page is visible (PLR rendered)."""
    page.wait_for_function(
        "() => { const el = document.querySelector('.plr-page'); "
        "return el && el.offsetParent !== null "
        "&& el.getBoundingClientRect().height > 0; }",
        timeout=timeout,
    )


def _make_plain_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("notes.md", "# Smoke Test\n\nSG/Send QA smoke test.")
        zf.writestr("data.txt", "smoke test data")
    buf.seek(0)
    return buf.read()


def _make_plr_zip() -> bytes:
    page_json = json.dumps({
        "title": "Smoke Test Layout",
        "sections": [
            {"type": "text", "title": "Smoke", "content": "QA smoke test — PLR rendering."}
        ]
    }, indent=2)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("_page.json", page_json)
        zf.writestr("notes.md", "# Notes\n\nSmoke test notes.")
    buf.seek(0)
    return buf.read()


# ── No-auth smoke tests ───────────────────────────────────────────────────────

class TestSmokeNoAuth:
    """Navigation-only smoke tests — no upload credentials required."""

    # SM-001
    def test_browse_page_loads(self, page, ui_url, screenshots):
        """SM-001: /en-gb/browse/ loads without errors."""
        page.goto(f"{ui_url}/en-gb/browse/", wait_until="domcontentloaded")
        page.wait_for_selector("body[data-ready]", timeout=20_000)
        screenshots.capture(page, "sm001_browse_loads", "Browse page loaded")

        assert page.locator("body").is_visible()
        assert "error" not in (page.inner_text("body") or "").lower()[:200]

    # SM-002
    def test_browse_entry_form_present(self, page, ui_url, screenshots):
        """SM-002: Entry form (input + Decrypt & Download) visible at /en-gb/browse/."""
        page.goto(f"{ui_url}/en-gb/browse/", wait_until="domcontentloaded")
        page.wait_for_selector("body[data-ready]", timeout=20_000)

        entry_input = page.locator("input").first
        assert entry_input.is_visible(), "Entry form input not visible"

        btn = page.get_by_role("button", name="Decrypt & Download")
        assert btn.is_visible(), "'Decrypt & Download' button not visible"
        screenshots.capture(page, "sm002_entry_form", "Entry form visible")

    # SM-003
    def test_download_page_loads(self, page, ui_url, screenshots):
        """SM-003: /en-gb/download/ loads and shows entry form."""
        page.goto(f"{ui_url}/en-gb/download/", wait_until="domcontentloaded")
        page.wait_for_selector("body[data-ready]", timeout=20_000)
        screenshots.capture(page, "sm003_download_page", "Download page loaded")

        page_text = page.inner_text("body") or ""
        assert any(kw in page_text.lower() for kw in ["decrypt", "download", "token", "key"]), \
            "Download page missing expected entry form text"

    # SM-004
    def test_ui_version_in_footer(self, page, ui_url, screenshots):
        """SM-004: Footer shows UI version (confirms v0.3.1 overlay is active)."""
        page.goto(f"{ui_url}/en-gb/browse/", wait_until="domcontentloaded")
        page.wait_for_selector("body[data-ready]", timeout=20_000)
        screenshots.capture(page, "sm004_footer_version", "Footer with UI version")

        page_text = page.inner_text("body") or ""
        assert "UI v" in page_text or "v0." in page_text, \
            f"UI version not found in footer. Page text snippet: {page_text[-300:]}"

    # SM-005
    def test_no_js_errors_on_browse(self, page, ui_url, screenshots):
        """SM-005: No uncaught JS errors when loading the browse page."""
        js_errors = []
        page.on("pageerror", lambda err: js_errors.append(str(err)))

        page.goto(f"{ui_url}/en-gb/browse/", wait_until="domcontentloaded")
        page.wait_for_selector("body[data-ready]", timeout=20_000)
        page.wait_for_timeout(2_000)
        screenshots.capture(page, "sm005_no_js_errors", f"JS errors: {js_errors or 'none'}")

        assert not js_errors, f"Uncaught JS errors on browse page: {js_errors}"

    # SM-006
    def test_sg_send_branding_present(self, page, ui_url, screenshots):
        """SM-006: SG/Send branding visible — confirms correct app is served."""
        page.goto(f"{ui_url}/en-gb/browse/", wait_until="domcontentloaded")
        page.wait_for_selector("body[data-ready]", timeout=20_000)
        screenshots.capture(page, "sm006_branding", "SG/Send branding")

        page_text = page.inner_text("body") or ""
        assert any(kw in page_text for kw in ["SG/Send", "SGraph", "sgraph"]), \
            "SG/Send branding not found on page"


# ── Upload smoke tests ────────────────────────────────────────────────────────

class TestSmokeUpload:
    """Round-trip smoke tests — require SG_SEND_ACCESS_TOKEN / --access-token."""

    # SM-010
    def test_upload_and_browse_tree_renders(self, page, ui_url, require_upload, screenshots):
        """SM-010: Upload zip → browse → file tree renders (catches SGMETA/zipTree regressions)."""
        tid, key = require_upload.upload_encrypted(_make_plain_zip(), "smoke-browse.zip")

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key}", wait_until="domcontentloaded")
        _wait_browse(page)
        screenshots.capture(page, "sm010_browse_tree", "Browse tree rendered")

        tree_items = page.locator(".sb-tree__file-name").all_text_contents()
        assert len(tree_items) > 0, "Browse tree is empty after upload — possible SGMETA regression"
        assert any("notes.md" in t for t in tree_items), \
            f"notes.md not in tree. Tree: {tree_items}"

    # SM-011
    def test_sgmeta_stripped_from_download(self, page, ui_url, require_upload, screenshots):
        """SM-011: Download page delivers clean file — SGMETA envelope is stripped.

        This directly tests the regression observed on dev.send.sgraph.ai (31 March 2026)
        where the download page served SGMETA-wrapped bytes instead of the clean file.
        """
        from pathlib import Path
        tid, key = require_upload.upload_encrypted(
            b"smoke test content - must not start with SGMETA",
            "smoke-download.txt",
        )

        with page.expect_download(timeout=60_000) as dl_info:
            page.goto(f"{ui_url}/en-gb/download/#{tid}/{key}", wait_until="domcontentloaded")

        download = dl_info.value
        content = Path(download.path()).read_bytes()
        screenshots.capture(page, "sm011_download_clean", "Download — SGMETA check")

        assert not content.startswith(b"SGMETA"), (
            "REGRESSION: Downloaded file starts with SGMETA magic bytes. "
            "The download page is not stripping the envelope. "
            f"First 20 bytes: {content[:20]!r}"
        )
        assert b"smoke test content" in content, \
            f"Expected content not in download. First 50 bytes: {content[:50]!r}"

    # SM-012
    def test_plr_auto_opens_page_json(self, page, ui_url, require_upload, screenshots):
        """SM-012: Upload zip with _page.json → PLR auto-opens and renders layout."""
        tid, key = require_upload.upload_encrypted(_make_plr_zip(), "smoke-plr.zip")

        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key}", wait_until="domcontentloaded")
        _wait_plr(page)
        screenshots.capture(page, "sm012_plr_rendered", "PLR auto-opened")

        assert page.locator(".plr-page").is_visible(), \
            ".plr-page not visible — PLR failed to render after upload"

    # SM-013
    def test_entry_form_resolves_transfer(self, page, ui_url, require_upload, screenshots):
        """SM-013: Entry form — enter tid/key → browse opens (catches entry form regressions)."""
        tid, key = require_upload.upload_encrypted(_make_plain_zip(), "smoke-entry.zip")

        page.goto(f"{ui_url}/en-gb/browse/", wait_until="domcontentloaded")
        page.wait_for_selector("body[data-ready]", timeout=30_000)

        entry_input = page.locator("input").first
        entry_input.wait_for(state="visible", timeout=10_000)
        entry_input.fill(f"{tid}/{key}")
        page.get_by_role("button", name="Decrypt & Download").click()

        _wait_browse(page)
        screenshots.capture(page, "sm013_entry_form_resolved", "Entry form resolved to browse")

        tree_items = page.locator(".sb-tree__file-name").all_text_contents()
        assert len(tree_items) > 0, \
            "Browse tree empty after entry form submit — possible regression"

    # SM-014
    def test_zip_download_is_valid(self, page, ui_url, require_upload, screenshots):
        """SM-014: Download page delivers a valid zip file (PK magic bytes, not SGMETA)."""
        import zipfile as zf_mod
        from pathlib import Path

        tid, key = require_upload.upload_encrypted(_make_plain_zip(), "smoke-zip-dl.zip")

        with page.expect_download(timeout=60_000) as dl_info:
            page.goto(f"{ui_url}/en-gb/download/#{tid}/{key}", wait_until="domcontentloaded")

        download = dl_info.value
        content = Path(download.path()).read_bytes()
        screenshots.capture(page, "sm014_zip_valid", "Downloaded zip — PK check")

        assert content.startswith(b"PK"), (
            f"Downloaded zip does not start with PK magic. "
            f"First 20 bytes: {content[:20]!r} — likely SGMETA not stripped."
        )
        try:
            buf = io.BytesIO(content)
            with zf_mod.ZipFile(buf) as z:
                names = z.namelist()
            assert len(names) > 0, "Downloaded zip is empty"
        except zf_mod.BadZipFile:
            assert False, (
                f"Downloaded file is not a valid zip. "
                f"First 20 bytes: {content[:20]!r}"
            )
