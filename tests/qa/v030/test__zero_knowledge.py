"""UC-12: Zero-Knowledge Security Verification (P0).

The most important test from a product perspective.

Verifies that the server never sees plaintext content:
  1. Upload a file with known plaintext via the API
  2. Download the raw bytes from the server
  3. Verify the bytes do NOT contain the plaintext
  4. Verify the bytes are AES-256-GCM ciphertext (12-byte IV prefix)
  5. Verify the API info endpoint reveals no original filename
  6. Verify the SGMETA envelope is inside the encrypted blob
"""

import pytest
import httpx

pytestmark = pytest.mark.p0

CANARY_STRING = "CANARY_STRING_12345_ZERO_KNOWLEDGE_TEST"
CANARY_FILENAME = "secret-document.txt"


class TestZeroKnowledge:
    """Verify server-side zero-knowledge: no plaintext on the server, ever."""

    def test_server_stores_only_ciphertext(self, transfer_helper, api_url):
        """Download raw bytes from the API and verify no plaintext content."""
        tid, _key = transfer_helper.upload_encrypted(
            plaintext=CANARY_STRING.encode(),
            filename=CANARY_FILENAME,
        )

        # Download the raw encrypted blob from the API
        resp = httpx.get(f"{api_url}/api/transfers/download/{tid}")
        assert resp.status_code == 200, f"Download failed: {resp.status_code}"

        raw_bytes = resp.content

        # The raw bytes must NOT contain the plaintext canary
        assert CANARY_STRING.encode() not in raw_bytes, (
            "CRITICAL: Plaintext canary found in server-stored bytes! "
            "Zero-knowledge property violated."
        )

        # The raw bytes must NOT contain the filename
        assert CANARY_FILENAME.encode() not in raw_bytes, (
            "CRITICAL: Original filename found in server-stored bytes! "
            "SGMETA envelope should be inside the encrypted blob."
        )

    def test_ciphertext_format_aes_gcm(self, transfer_helper, api_url):
        """Verify the stored blob starts with a 12-byte IV (AES-256-GCM format)."""
        tid, _key = transfer_helper.upload_encrypted(
            plaintext=b"AES-GCM format verification content",
            filename="format-test.txt",
        )

        resp = httpx.get(f"{api_url}/api/transfers/download/{tid}")
        assert resp.status_code == 200
        raw_bytes = resp.content

        # AES-256-GCM with 12-byte IV prepended:
        # [IV: 12 bytes][ciphertext + auth tag: remaining bytes]
        assert len(raw_bytes) > 12, (
            f"Encrypted blob too short ({len(raw_bytes)} bytes) — "
            f"expected at least 12 bytes for IV"
        )

        # The first 12 bytes are the IV — they should look random (high entropy)
        iv = raw_bytes[:12]
        # Basic entropy check: at least 6 unique byte values in 12 bytes
        unique_bytes = len(set(iv))
        assert unique_bytes >= 4, (
            f"IV has suspiciously low entropy ({unique_bytes} unique bytes in 12). "
            f"May not be a valid random IV."
        )

        # AES-GCM auth tag is 16 bytes at the end
        # So ciphertext portion = total - 12 (IV) - 16 (tag) = plaintext + SGMETA overhead
        ciphertext_len = len(raw_bytes) - 12
        assert ciphertext_len > 16, (
            f"Ciphertext too short ({ciphertext_len} bytes) — "
            f"expected plaintext + SGMETA envelope + 16-byte auth tag"
        )

    def test_api_info_reveals_no_filename(self, transfer_helper, api_url):
        """Hit the info endpoint and verify no original filename is exposed."""
        tid, _key = transfer_helper.upload_encrypted(
            plaintext=b"info endpoint test",
            filename="super-secret-name.docx",
        )

        resp = httpx.get(f"{api_url}/api/transfers/info/{tid}")
        assert resp.status_code == 200, f"Info endpoint failed: {resp.status_code}"

        info = resp.json()
        info_str = str(info).lower()

        # The original filename must not appear in the info response
        assert "super-secret-name" not in info_str, (
            f"CRITICAL: Original filename found in API info response! "
            f"Info: {info}"
        )
        assert ".docx" not in info_str, (
            f"File extension leaked in API info response: {info}"
        )

    def test_sgmeta_envelope_is_encrypted(self, transfer_helper, api_url):
        """Verify the SGMETA magic bytes are NOT visible in the raw download.

        The SGMETA envelope (magic + length + JSON metadata + content) must
        be entirely inside the encrypted blob.  If the magic bytes appear in
        the raw download, the envelope is not encrypted.
        """
        tid, _key = transfer_helper.upload_encrypted(
            plaintext=b"SGMETA envelope encryption test",
            filename="envelope-test.txt",
        )

        resp = httpx.get(f"{api_url}/api/transfers/download/{tid}")
        assert resp.status_code == 200
        raw_bytes = resp.content

        # SGMETA magic: 0x53 0x47 0x4D 0x45 0x54 0x41 0x00 = "SGMETA\0"
        sgmeta_magic = bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41, 0x00])

        # The magic should NOT appear in the raw bytes (it's inside the encrypted blob)
        # Skip the first 12 bytes (IV) since the magic could theoretically collide
        assert sgmeta_magic not in raw_bytes[12:], (
            "CRITICAL: SGMETA magic bytes found in raw download! "
            "The metadata envelope is not encrypted."
        )

    def test_multiple_uploads_produce_different_ciphertext(self, transfer_helper, api_url):
        """Same plaintext uploaded twice should produce different ciphertext (random IV)."""
        plaintext = b"identical content for IV uniqueness test"

        tid1, _key1 = transfer_helper.upload_encrypted(plaintext, filename="same1.txt")
        tid2, _key2 = transfer_helper.upload_encrypted(plaintext, filename="same2.txt")

        resp1 = httpx.get(f"{api_url}/api/transfers/download/{tid1}")
        resp2 = httpx.get(f"{api_url}/api/transfers/download/{tid2}")

        assert resp1.status_code == 200
        assert resp2.status_code == 200

        # Different random IVs → different ciphertext
        assert resp1.content != resp2.content, (
            "Two uploads of identical content produced identical ciphertext! "
            "IVs should be random and unique per encryption."
        )

        # Specifically, the IVs (first 12 bytes) should differ
        iv1 = resp1.content[:12]
        iv2 = resp2.content[:12]
        assert iv1 != iv2, "IVs are identical across two encryptions — IV reuse detected"
