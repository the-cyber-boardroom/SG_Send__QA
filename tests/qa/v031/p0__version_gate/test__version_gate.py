"""P0: v0.3.1 version gate.

These tests run first. They assert that the locally-served UI is actually
v0.3.1 and that all overlay files are present. If any gate test fails, all
BRW-* tests in this suite are meaningless — a CI failure here means the
overlay was not deployed or the wrong UI version is installed.

Checks:
  - window.SGRAPH_BUILD.uiVersion === 'v0.3.1' on upload page
  - window.SGRAPH_BUILD.uiVersion === 'v0.3.1' on browse page
  - All 5 overlay files are served (no 404 fallback to v0.3.0 behaviour)
"""

import pytest

pytestmark = [pytest.mark.p0, pytest.mark.v031]

_OVERLAY_FILES = [
    "send-browse-v031.js",
    "send-browse-v031.css",
    "markdown-parser-v031.js",
    "send-gallery-v031.js",
    "upload-folder-v031.js",
]


class TestVersionGate:
    """Assert v0.3.1 UI is active before running any BRW-* tests."""

    def test_upload_page_reports_v031(self, page, ui_url, screenshots):
        """Upload page (en-gb/) sets window.SGRAPH_BUILD.uiVersion = 'v0.3.1'."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        version = page.evaluate("() => window.SGRAPH_BUILD?.uiVersion")
        screenshots.capture(page, "01_upload_version", f"Upload page version: {version}")
        assert version == "v0.3.1", (
            f"Upload page reports version {version!r} — expected v0.3.1. "
            "Is the v0.3.1 UI package installed?"
        )

    def test_browse_page_reports_v031(self, page, ui_url, screenshots):
        """Browse page (en-gb/browse/) sets window.SGRAPH_BUILD.uiVersion = 'v0.3.1'."""
        page.goto(f"{ui_url}/en-gb/browse/")
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        version = page.evaluate("() => window.SGRAPH_BUILD?.uiVersion")
        screenshots.capture(page, "02_browse_version", f"Browse page version: {version}")
        assert version == "v0.3.1", (
            f"Browse page reports version {version!r} — expected v0.3.1. "
            "Check that send-browse-v031.js is served and not returning 404."
        )

    def test_browse_overlay_files_loaded(self, page, ui_url, transfer_helper, screenshots):
        """All 5 v0.3.1 overlay files are fetched with HTTP 200 on the browse page."""
        import zipfile, io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("file.txt", "content")
        buf.seek(0)
        tid, key_b64 = transfer_helper.upload_encrypted(buf.read(), "file.zip")

        loaded_200 = set()

        def _on_response(response):
            filename = response.url.split("/")[-1].split("?")[0]
            if response.status == 200:
                loaded_200.add(filename)

        page.on("response", _on_response)
        page.goto(f"{ui_url}/en-gb/browse/#{tid}/{key_b64}")
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1_000)  # allow deferred script loads

        screenshots.capture(page, "03_network_overlays", "Browse page with overlay files")

        missing = [f for f in _OVERLAY_FILES if f not in loaded_200]
        assert not missing, (
            f"v0.3.1 overlay files not loaded (HTTP 200) on browse page: {missing}. "
            "These files are required — without them the page falls back to v0.3.0."
        )
