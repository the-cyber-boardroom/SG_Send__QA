"""BUG: Download page serves SGMETA envelope bytes in the downloaded file.

Observed at: dev.send.sgraph.ai/en-gb/download/#help-aunt-2780 (31 March 2026)
NOT reproduced on local test server (installed package may have the fix already).

Symptom:
  The download page decrypts the transfer correctly, but the file handed to
  the browser contains the raw SGMETA envelope prepended to the file content:

      SGMETA{"filename": "vault-snapshot.zip"}PK...

  The user receives a corrupt file — it is the SGMETA-wrapped payload, not
  the original file. On a zip transfer the result starts with SGMETA instead
  of PK (zip magic bytes).

Root cause (suspected):
  The download page's decrypt path creates a Blob from the raw decrypted buffer
  without first stripping the SGMETA envelope.

  SGMETA format:
      magic(6 bytes: 0x53 0x47 0x4D 0x45 0x54 0x41 = "SGMETA")
    + length(4 bytes big-endian: byte count of JSON metadata)
    + metadata(JSON: {"filename": "..."})
    + file_content

  Fix: parse and discard the SGMETA header before creating the download Blob.

Environment note:
  Local test server (installed package) returns a clean file — SGMETA is
  stripped and the downloaded zip starts with PK (valid zip magic). The bug
  was observed on dev.send.sgraph.ai, suggesting dev is behind the installed
  version. This test will PASS against a build that has the bug and FAIL
  against a build with the fix (the installed package).

Bug test pattern:
  PASSES while the bug exists (download contains SGMETA bytes).
  FAILS when fixed (download is clean) → delete this file and add a proper
  positive assertion to the main download test suite.
"""

import io
import zipfile
from pathlib import Path

import pytest

pytestmark = [pytest.mark.p0, pytest.mark.v031]

_SGMETA_MAGIC = b"SGMETA"


def _make_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("notes.md", "# hello")
        zf.writestr("_page.json", '{"title": "test"}')
    buf.seek(0)
    return buf.read()


class TestBugDownloadSGMETANotStripped:
    """BUG: SGMETA envelope not stripped from download page output."""

    @pytest.fixture(autouse=True)
    def _setup(self, transfer_helper, ui_url):
        self._tid, self._key = transfer_helper.upload_encrypted(
            _make_zip(), "vault-snapshot.zip", content_type="application/zip"
        )
        self._url = f"{ui_url}/en-gb/download/#{self._tid}/{self._key}"

    def test_p0_bug_download_starts_with_sgmeta(self, page, screenshots):
        """BUG: Downloaded zip starts with SGMETA magic bytes (envelope not stripped).

        PASSES while the bug exists (content starts with SGMETA, not PK).
        FAILS when fixed (content starts with PK — valid zip) → delete this file.

        Note: as of 31 March 2026, local test server has this fixed. This test
        reproduces the bug observed on dev.send.sgraph.ai.
        """
        with page.expect_download(timeout=30_000) as dl_info:
            page.goto(self._url)

        download = dl_info.value
        screenshots.capture(page, "dl_bug_01_page_state", "Download page after decrypt")

        path = Path(download.path())
        content = path.read_bytes()

        screenshots.capture(
            page, "dl_bug_02_downloaded",
            f"Downloaded: {download.suggested_filename!r} — "
            f"starts_with_SGMETA={content.startswith(_SGMETA_MAGIC)} "
            f"first_bytes={content[:6]!r}"
        )

        # BUG ASSERTION: file starts with SGMETA (envelope not stripped).
        # PASSES while bug exists. FAILS when fixed.
        assert content.startswith(_SGMETA_MAGIC), (
            "BUG FIXED: Downloaded file does NOT start with SGMETA magic bytes — "
            "the download page is now stripping the envelope correctly. "
            "Delete this bug test file and add a positive regression assertion "
            "to the main download test suite."
        )

    def test_p0_bug_download_is_not_valid_zip(self, page, screenshots):
        """BUG: Downloaded zip is not a valid zip (first bytes are SGMETA, not PK).

        A valid zip starts with PK (0x50 0x4B). When the SGMETA envelope is NOT
        stripped, the file starts with SGMETA instead — making it an invalid zip.

        PASSES while bug exists (not a valid zip).
        FAILS when fixed (valid zip starts with PK) → delete this file.
        """
        with page.expect_download(timeout=30_000) as dl_info:
            page.goto(self._url)

        download = dl_info.value
        path = Path(download.path())
        content = path.read_bytes()

        # BUG ASSERTION: file does NOT start with PK (zip magic).
        # PASSES while bug exists. FAILS when fixed.
        assert not content.startswith(b"PK"), (
            "BUG FIXED: Downloaded file starts with PK (valid zip magic). "
            "The download page is now delivering a clean zip. "
            "Delete this bug test file."
        )
