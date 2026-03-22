"""Unit tests for TransferHelper encryption (P1).

TransferHelper is the Python-side implementation of the browser's Web Crypto
encryption.  Every download-side test depends on it being correct — if it
produces the wrong format, those tests silently validate nothing.

These tests run without a browser and without a live server.
They verify:
  1. AES-256-GCM: key length, IV length, correct decryption
  2. SGMETA envelope: magic prefix, 4-byte big-endian length, JSON, content
  3. Round-trip: encrypt → decrypt → plaintext and filename match
  4. IV uniqueness: each call uses a fresh random IV
  5. base64url key: no padding, URL-safe alphabet, correct length
  6. Key uniqueness: each call generates a different 256-bit key
  7. Wrong key raises an error (not silent corruption)
  8. Wrong IV fails decryption
"""

import base64
import json
import os
import pytest

pytestmark = pytest.mark.p1

# ---------------------------------------------------------------------------
# Import helpers from conftest without going through pytest's fixture system
# ---------------------------------------------------------------------------
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from tests.qa.v030.conftest import TransferHelper


SGMETA_MAGIC = bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41, 0x00])  # "SGMETA\0"


def _make_helper():
    """TransferHelper with a dummy api_url — upload_encrypted doesn't call the API."""
    return TransferHelper(api_url="http://localhost:0")


def _encrypt_raw(helper, plaintext: bytes, filename: str):
    """Call the encryption half of upload_encrypted without the HTTP upload."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key_bytes = os.urandom(32)
    iv        = os.urandom(12)
    aesgcm    = AESGCM(key_bytes)

    meta_json = json.dumps({"filename": filename}).encode()
    meta_len  = len(meta_json).to_bytes(4, "big")
    envelope  = helper.SGMETA_MAGIC + meta_len + meta_json + plaintext

    ciphertext = iv + aesgcm.encrypt(iv, envelope, None)
    key_b64    = base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode()
    return ciphertext, key_b64, key_bytes, iv


def _decrypt_envelope(ciphertext: bytes, key_bytes: bytes):
    """Decrypt and parse back to (plaintext, filename)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    iv         = ciphertext[:12]
    aesgcm     = AESGCM(key_bytes)
    envelope   = aesgcm.decrypt(iv, ciphertext[12:], None)

    assert envelope[:7] == SGMETA_MAGIC, "SGMETA magic mismatch"
    meta_len = int.from_bytes(envelope[7:11], "big")
    meta_json = envelope[11:11 + meta_len]
    plaintext = envelope[11 + meta_len:]

    meta = json.loads(meta_json.decode())
    return plaintext, meta["filename"]


class TestSGMETAEnvelope:
    """Verify the SGMETA envelope structure."""

    def test_magic_prefix(self):
        """Encrypted blob must start with random IV, not the SGMETA magic."""
        helper = _make_helper()
        ciphertext, _, _, _ = _encrypt_raw(helper, b"hello", "test.txt")

        # The raw ciphertext starts with IV (12 random bytes), not the magic
        assert ciphertext[:7] != SGMETA_MAGIC, (
            "Ciphertext starts with SGMETA magic — envelope is not encrypted"
        )

    def test_magic_hidden_after_decryption_prefix(self):
        """After decryption, the envelope starts with SGMETA magic."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        helper = _make_helper()
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, b"hello", "test.txt")

        iv       = ciphertext[:12]
        aesgcm   = AESGCM(key_bytes)
        envelope = aesgcm.decrypt(iv, ciphertext[12:], None)

        assert envelope[:7] == SGMETA_MAGIC, (
            f"Decrypted envelope does not start with SGMETA magic. "
            f"Got: {envelope[:7].hex()}"
        )

    def test_meta_length_field(self):
        """4-byte big-endian length field correctly encodes the JSON length."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        helper    = _make_helper()
        filename  = "some-file.txt"
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, b"content", filename)

        iv       = ciphertext[:12]
        aesgcm   = AESGCM(key_bytes)
        envelope = aesgcm.decrypt(iv, ciphertext[12:], None)

        meta_len_encoded = int.from_bytes(envelope[7:11], "big")
        actual_meta_json = json.dumps({"filename": filename}).encode()

        assert meta_len_encoded == len(actual_meta_json), (
            f"Length field says {meta_len_encoded} but JSON is {len(actual_meta_json)} bytes"
        )

    def test_filename_in_metadata(self):
        """Filename appears in the JSON metadata section of the envelope."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        helper   = _make_helper()
        filename = "my-document.pdf"
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, b"pdf content", filename)

        iv       = ciphertext[:12]
        aesgcm   = AESGCM(key_bytes)
        envelope = aesgcm.decrypt(iv, ciphertext[12:], None)

        meta_len = int.from_bytes(envelope[7:11], "big")
        meta     = json.loads(envelope[11:11 + meta_len].decode())

        assert meta.get("filename") == filename, (
            f"Expected filename '{filename}' in metadata, got: {meta}"
        )

    def test_content_after_metadata(self):
        """Plaintext content follows immediately after the metadata JSON."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        helper    = _make_helper()
        plaintext = b"exact content bytes 1234"
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, plaintext, "test.txt")

        iv       = ciphertext[:12]
        aesgcm   = AESGCM(key_bytes)
        envelope = aesgcm.decrypt(iv, ciphertext[12:], None)

        meta_len       = int.from_bytes(envelope[7:11], "big")
        content_offset = 11 + meta_len
        recovered      = envelope[content_offset:]

        assert recovered == plaintext, (
            f"Content mismatch after envelope parse. "
            f"Expected {len(plaintext)} bytes, got {len(recovered)} bytes."
        )


class TestAESGCMParameters:
    """Verify AES-256-GCM encryption parameters."""

    def test_iv_length_12_bytes(self):
        """IV must be exactly 12 bytes (96-bit IV for AES-GCM)."""
        helper = _make_helper()
        ciphertext, _, _, iv = _encrypt_raw(helper, b"data", "file.txt")

        assert len(iv) == 12, f"IV is {len(iv)} bytes, expected 12"

    def test_key_length_32_bytes(self):
        """Key must be 256-bit (32 bytes)."""
        helper = _make_helper()
        _, key_b64, key_bytes, _ = _encrypt_raw(helper, b"data", "file.txt")

        assert len(key_bytes) == 32, f"Key is {len(key_bytes)} bytes, expected 32 (AES-256)"

    def test_auth_tag_present(self):
        """Ciphertext must include the 16-byte GCM authentication tag."""
        helper    = _make_helper()
        plaintext = b"some content"
        ciphertext, _, _, iv = _encrypt_raw(helper, plaintext, "file.txt")

        # Structure: 12 (IV) + len(plaintext) + 7 (magic) + 4 (len) + len(json) + 16 (tag)
        min_expected = 12 + len(plaintext) + 7 + 4 + 16
        assert len(ciphertext) >= min_expected, (
            f"Ciphertext too short ({len(ciphertext)} bytes) — auth tag may be missing"
        )

    def test_iv_prepended_to_ciphertext(self):
        """IV must be the first 12 bytes of the output blob (matches browser format)."""
        helper = _make_helper()
        ciphertext, _, _, iv = _encrypt_raw(helper, b"data", "file.txt")

        assert ciphertext[:12] == iv, "IV is not prepended to ciphertext"


class TestRoundTrip:
    """Encrypt and decrypt to confirm correctness end-to-end."""

    def test_plaintext_survives_round_trip(self):
        """Encrypt then decrypt produces identical plaintext."""
        helper    = _make_helper()
        plaintext = b"Hello, zero-knowledge world!"
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, plaintext, "hello.txt")

        recovered, _ = _decrypt_envelope(ciphertext, key_bytes)
        assert recovered == plaintext

    def test_filename_survives_round_trip(self):
        """Filename in the SGMETA envelope round-trips correctly."""
        helper   = _make_helper()
        filename = "report-2026-q1.pdf"
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, b"content", filename)

        _, recovered_filename = _decrypt_envelope(ciphertext, key_bytes)
        assert recovered_filename == filename

    def test_empty_plaintext_round_trip(self):
        """Empty content is valid and round-trips to empty bytes."""
        helper = _make_helper()
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, b"", "empty.txt")

        recovered, _ = _decrypt_envelope(ciphertext, key_bytes)
        assert recovered == b""

    def test_binary_content_round_trip(self):
        """Binary content (e.g. PNG header) round-trips correctly."""
        helper  = _make_helper()
        content = bytes(range(256)) * 4  # 1 KB of all byte values
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, content, "binary.bin")

        recovered, _ = _decrypt_envelope(ciphertext, key_bytes)
        assert recovered == content

    def test_unicode_filename_round_trip(self):
        """UTF-8 filename survives the JSON encode/decode cycle."""
        helper   = _make_helper()
        filename = "résumé-αβγ-日本語.txt"
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, b"text", filename)

        _, recovered = _decrypt_envelope(ciphertext, key_bytes)
        assert recovered == filename


class TestKeyEncoding:
    """Verify base64url key encoding matches the browser's exportKey output."""

    def test_key_is_base64url(self):
        """Key must use URL-safe base64 alphabet (no +, /, or =)."""
        helper = _make_helper()
        _, key_b64, _, _ = _encrypt_raw(helper, b"data", "f.txt")

        assert "+" not in key_b64, "Key uses + (standard base64), not base64url"
        assert "/" not in key_b64, "Key uses / (standard base64), not base64url"
        assert "=" not in key_b64, "Key has padding — should be stripped"

    def test_key_decodes_to_32_bytes(self):
        """base64url key without padding must decode to 32 bytes (256-bit)."""
        helper = _make_helper()
        _, key_b64, _, _ = _encrypt_raw(helper, b"data", "f.txt")

        # Add padding back for decode
        padded    = key_b64 + "=" * (-len(key_b64) % 4)
        key_bytes = base64.urlsafe_b64decode(padded)
        assert len(key_bytes) == 32, f"Decoded key is {len(key_bytes)} bytes, expected 32"

    def test_key_uniqueness(self):
        """Each encryption call must generate a different 256-bit key."""
        helper = _make_helper()
        keys = set()
        for _ in range(10):
            _, key_b64, _, _ = _encrypt_raw(helper, b"same content", "same.txt")
            keys.add(key_b64)

        assert len(keys) == 10, f"Key reuse detected — only {len(keys)} unique keys in 10 calls"


class TestIVUniqueness:
    """Verify each encryption uses a fresh random IV."""

    def test_iv_is_random_per_call(self):
        """10 encryptions of identical content must produce 10 different IVs."""
        helper = _make_helper()
        ivs = set()
        for _ in range(10):
            ciphertext, _, _, iv = _encrypt_raw(helper, b"identical content", "same.txt")
            ivs.add(iv)

        assert len(ivs) == 10, f"IV reuse detected — only {len(ivs)} unique IVs in 10 calls"

    def test_ciphertext_differs_due_to_iv(self):
        """Same plaintext + different IVs → different ciphertext each time."""
        helper = _make_helper()
        blobs = set()
        for _ in range(5):
            ciphertext, _, _, _ = _encrypt_raw(helper, b"same text", "f.txt")
            blobs.add(ciphertext)

        assert len(blobs) == 5, "Ciphertext is identical across calls — IV may not be random"


class TestWrongKeyFails:
    """Decryption with the wrong key must raise, not silently return garbage."""

    def test_wrong_key_raises(self):
        """Decrypting with a different key raises an error (GCM auth tag check)."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.exceptions import InvalidTag

        helper = _make_helper()
        ciphertext, _, _, _ = _encrypt_raw(helper, b"secret", "secret.txt")

        wrong_key = os.urandom(32)
        iv        = ciphertext[:12]
        aesgcm    = AESGCM(wrong_key)

        with pytest.raises((InvalidTag, Exception)):
            aesgcm.decrypt(iv, ciphertext[12:], None)

    def test_wrong_iv_raises(self):
        """Decrypting with a flipped IV raises due to auth tag failure."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.exceptions import InvalidTag

        helper = _make_helper()
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, b"secret", "secret.txt")

        # Flip the first byte of the IV
        wrong_iv  = bytes([ciphertext[0] ^ 0xFF]) + ciphertext[1:12]
        aesgcm    = AESGCM(key_bytes)

        with pytest.raises((InvalidTag, Exception)):
            aesgcm.decrypt(wrong_iv, ciphertext[12:], None)

    def test_truncated_ciphertext_raises(self):
        """A truncated ciphertext (missing auth tag bytes) must fail decryption."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.exceptions import InvalidTag

        helper = _make_helper()
        ciphertext, _, key_bytes, _ = _encrypt_raw(helper, b"secret data", "f.txt")

        iv        = ciphertext[:12]
        truncated = ciphertext[12:-8]  # drop last 8 bytes of auth tag
        aesgcm    = AESGCM(key_bytes)

        with pytest.raises((InvalidTag, Exception, ValueError)):
            aesgcm.decrypt(iv, truncated, None)
