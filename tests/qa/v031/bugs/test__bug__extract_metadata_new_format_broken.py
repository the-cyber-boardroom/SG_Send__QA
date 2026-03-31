"""BUG (P0): _extractMetadata broken for new-format SGMETA payloads — v0.20.29

Introduced by: commit a28e8206 ("fix: handle old SGMETA wire format")
Observed: 31 March 2026 — all browse tests fail (zipTree=0) after installing v0.20.29

Root cause:
  The SGMETA fix uses bytes[6] !== 0x00 to detect new vs old format:

      if (bytes[magic.length] !== 0x00) { /* new format */ }
      // else: old format (bytes[magic.length] === 0x00)

  BUT — in the NEW format, the first byte of the 4-byte length field is at
  position 6 (immediately after the 6-byte magic). For any metadata JSON
  smaller than 16 MB (which is every real payload), the big-endian 4-byte
  length starts with 0x00. So:

      New format: SGMETA[6] + 0x00{len_byte1} + 0x00{len_byte2} + ... + JSON + content
      Old format: SGMETA[6] + 0x00{separator} + {JSON}...

  bytes[6] === 0x00 for BOTH formats → new format always falls into the old
  format path.

  In the old format path, bytes[7] is expected to be '{' (0x7B). For new format,
  bytes[7] is the second byte of the 4-byte length (0x00 for JSON < 65 KB).
  Since 0x00 !== '{', the function returns { metadata: null, content: buf },
  i.e. the full SGMETA-wrapped buffer as "content".

Consequences:
  1. this.fileName is not set from SGMETA metadata (filename unknown)
  2. this.decryptedBytes = full SGMETA-wrapped buffer (not clean file content)
  3. For zip transfers: JSZip.loadAsync(SGMETA_wrapped_bytes) fails
     → this._zipTree = []  → browse tree never renders → state='complete', zipTree=0

Correct fix:
  Discriminate by checking bytes[7] (the byte after the potential null):
  - Old format: bytes[6]=0x00 AND bytes[7]=0x7B ('{')  → SGMETA\x00{json}
  - New format: bytes[6]=0x00 AND bytes[7]!=0x7B       → SGMETA + length[4] + json

  New discriminator: if (bytes[magic.length] !== 0x00 || bytes[magic.length+1] !== 0x7B)
  → new format (either bytes[6]!=0 OR bytes[6]=0 but bytes[7]!='{')

Bug test pattern:
  PASSES while bug exists (browse tree is empty / zipTree=0 for new-format transfer).
  FAILS when fixed (browse tree renders correctly) → delete this file.
"""

import io
import zipfile

import pytest

pytestmark = [pytest.mark.p0, pytest.mark.v031]


def _make_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("notes.md", "# Hello\n\nTest content.")
    buf.seek(0)
    return buf.read()


class TestBugExtractMetadataNewFormatBroken:
    """BUG: new-format SGMETA payloads not parsed correctly — browse tree empty."""

    @pytest.fixture(autouse=True)
    def _setup(self, transfer_helper, ui_url):
        # QA_Transfer_Helper uses NEW format: SGMETA + length(4) + JSON + content
        tid, key = transfer_helper.upload_encrypted(_make_zip(), "browse-test.zip")
        self._url = f"{ui_url}/en-gb/browse/#{tid}/{key}"

    def test_p0_bug_new_format_zip_tree_empty(self, page, screenshots):
        """BUG: New-format zip transfer has empty browse tree (zipTree=0) after decrypt.

        The _extractMetadata fix treats new-format payloads as old-format because
        both have bytes[6]=0x00. The parsing fails → content = full SGMETA buffer
        → JSZip parse fails → zipTree=0.

        PASSES while bug exists (zipTree=0).
        FAILS when fixed (zipTree>0, browse tree renders) → delete this file.
        """
        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=15_000)
        page.wait_for_timeout(3_000)

        screenshots.capture(page, "new_fmt_bug_01_state", "Browse state after decrypt")

        zip_tree_len = page.evaluate("""() => {
            const sd = document.querySelector('send-download');
            return sd ? (sd._zipTree || []).length : -1;
        }""")
        state = page.evaluate("""() => {
            const sd = document.querySelector('send-download');
            return sd ? sd.state : 'no send-download';
        }""")

        screenshots.capture(
            page, "new_fmt_bug_02_diag",
            f"state={state!r} zipTree={zip_tree_len}"
        )

        # BUG ASSERTION: zipTree is 0 (SGMETA not stripped, JSZip parse failed).
        # PASSES while bug exists. FAILS when fixed.
        assert zip_tree_len == 0, (
            "BUG FIXED: zipTree is non-zero — _extractMetadata correctly parsed "
            "the new-format SGMETA envelope and JSZip loaded the zip tree. "
            "Delete this bug test file."
        )

    def test_p0_bug_new_format_browse_tree_not_visible(self, page, screenshots):
        """BUG: Browse file tree is empty after new-format decrypt.

        PASSES while bug exists (no .sb-tree__file-name elements).
        FAILS when fixed (file names visible in tree) → delete this file.
        """
        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=15_000)
        page.wait_for_timeout(3_000)

        tree_items = page.locator(".sb-tree__file-name").all_text_contents()
        screenshots.capture(page, "new_fmt_bug_03_tree", f"Tree items: {tree_items}")

        # BUG ASSERTION: no file names in tree.
        # PASSES while bug exists. FAILS when fixed.
        assert len(tree_items) == 0, (
            "BUG FIXED: File names are visible in the browse tree — "
            "_extractMetadata correctly stripped the new-format SGMETA envelope. "
            "Delete this bug test file."
        )
