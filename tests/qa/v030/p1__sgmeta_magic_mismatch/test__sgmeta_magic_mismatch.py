"""BUG: SGMETA magic bytes mismatch between Python helper and JS upload component.

Severity: Medium (affects TransferHelper.upload_encrypted in QA test helpers only,
          not production uploads which go browser → JS → server → JS).

Root cause:
  The Python TransferHelper in conftest.py originally used a 7-byte SGMETA magic
  sequence (SGMETA + null terminator = 0x53 0x47 0x4D 0x45 0x54 0x41 0x00) while
  the JS upload component (upload-constants.js) and JS download component
  (send-download.js) both use a 6-byte sequence (0x53 0x47 0x4D 0x45 0x54 0x41).

  Effect: when downloading a TransferHelper-created transfer, the JS _extractMetadata()
  reads the length field from the wrong offset, parses an empty JSON string, throws,
  and falls back to { metadata: null, content: full_buffer }.  This means:
    - filename is not extracted from metadata → generic filename used
    - content bytes include the SGMETA header garbage when displayed inline

Status: FIXED in conftest.py — SGMETA_MAGIC changed to 6 bytes (no null terminator).

This file documents the bug and verifies the fix with a regression test.
"""

import pytest
import os
import json
import base64

pytestmark = pytest.mark.p1


class TestSgmetaMagicMismatch:
    """Regression tests for SGMETA magic byte mismatch (was 7 bytes, now 6 bytes)."""

    def test_transfer_helper_sgmeta_magic_is_6_bytes(self, transfer_helper):
        """Verify TransferHelper uses the correct 6-byte SGMETA magic (matches JS)."""
        assert len(transfer_helper.SGMETA_MAGIC) == 6, (
            f"SGMETA_MAGIC should be 6 bytes to match JS upload-constants.js, "
            f"got {len(transfer_helper.SGMETA_MAGIC)} bytes: {list(transfer_helper.SGMETA_MAGIC)}"
        )
        expected = bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41])  # "SGMETA"
        assert transfer_helper.SGMETA_MAGIC == expected, (
            f"SGMETA_MAGIC bytes mismatch. Expected {list(expected)}, "
            f"got {list(transfer_helper.SGMETA_MAGIC)}"
        )

    def test_api_created_transfer_decrypts_with_correct_filename(
        self, page, ui_url, transfer_helper, screenshots
    ):
        """API-created transfer should display with correct filename after decryption.

        With the 7-byte magic bug, metadata extraction failed and filename was lost.
        With the 6-byte fix, the filename 'sgmeta-regression.txt' is correctly
        extracted from the SGMETA envelope and displayed in the viewer.
        """
        from tests.qa.v030.browser_helpers import goto, handle_access_gate

        tid, key_b64 = transfer_helper.upload_encrypted(
            plaintext=b"SGMETA regression test content.",
            filename="sgmeta-regression.txt",
            content_type="text/plain",
        )
        browse_url = f"{ui_url}/en-gb/browse/#{tid}/{key_b64}"
        goto(page, browse_url)
        page.wait_for_timeout(4000)
        screenshots.capture(page, "01_sgmeta_regression", "SGMETA regression test — filename check")

        body_text = page.text_content("body") or ""
        assert "SGMETA regression test content." in body_text, (
            f"Decrypted content not found — possible SGMETA parsing failure. "
            f"Body snippet: {body_text[:300]}"
        )
        # Filename should appear in the UI header
        assert "sgmeta-regression.txt" in body_text, (
            f"Filename not visible — metadata extraction likely failed. "
            f"Body snippet: {body_text[:300]}"
        )
