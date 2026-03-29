"""Encrypted transfer helper for SG/Send QA.

Provides the single canonical TransferHelper implementation,
extracted from tests/qa/v030/conftest.py.

Creates real encrypted transfers via the SG/Send API without a browser,
matching the browser's Web Crypto encryption exactly:
  - AES-256-GCM, 12-byte random IV prepended to ciphertext
  - SGMETA envelope: magic(6) + length(4) + JSON metadata + content

Usage:
    from sg_send_qa.utils.QA_Transfer_Helper import QA_Transfer_Helper

    helper = QA_Transfer_Helper(api_url="http://...", access_token="tok")
    tid, key_b64 = helper.upload_encrypted(b"hello", filename="hi.txt")
"""

import os
import json
import base64

import httpx
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self as Type_Safe


class QA_Transfer_Helper(Type_Safe):
    """Create real encrypted transfers via the API without a browser.

    Matches the browser's Web Crypto encryption exactly:
      - AES-256-GCM, 12-byte random IV prepended to ciphertext
      - SGMETA envelope: magic(6) + length(4) + JSON metadata + content
    """

    # SGMETA magic bytes — 6 bytes, matches JS upload-constants.js
    SGMETA_MAGIC: bytes = bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41])

    api_url      : str   = ""
    access_token : str   = ""
    timeout      : float = 30.0   # seconds; default httpx 5s is too short through an egress proxy

    def _headers(self) -> dict:
        headers = {}
        if self.access_token:
            headers["x-sgraph-access-token"] = self.access_token
        return headers

    def create_and_complete(self, payload: bytes,
                            content_type: str = "application/octet-stream") -> str:
        """Create → upload → complete a transfer. Returns transfer_id."""
        create_resp = httpx.post(
            f"{self.api_url}/api/transfers/create",
            json    = {"file_size_bytes": len(payload), "content_type_hint": content_type},
            headers = self._headers(),
            timeout = self.timeout,
        )
        create_resp.raise_for_status()
        tid = create_resp.json()["transfer_id"]

        httpx.post(
            f"{self.api_url}/api/transfers/upload/{tid}",
            content = payload,
            headers = {**self._headers(), "content-type": "application/octet-stream"},
            timeout = self.timeout,
        ).raise_for_status()

        httpx.post(
            f"{self.api_url}/api/transfers/complete/{tid}",
            headers = self._headers(),
            timeout = self.timeout,
        ).raise_for_status()

        return tid

    def upload_encrypted(self, plaintext: bytes, filename: str = "test.txt",
                         content_type: str = "text/plain") -> tuple[str, str]:
        """Encrypt client-side (matching browser Web Crypto), upload.

        Returns (transfer_id, base64url_key).

        content_type is the ORIGINAL file type (before encryption).
        The download page uses this to decide whether to display inline
        (text/plain, image/*, application/pdf) or trigger a download.
        """
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        key_bytes = os.urandom(32)
        iv        = os.urandom(12)
        aesgcm    = AESGCM(key_bytes)

        # Build SGMETA envelope
        meta_json = json.dumps({"filename": filename}).encode()
        meta_len  = len(meta_json).to_bytes(4, "big")
        envelope  = self.SGMETA_MAGIC + meta_len + meta_json + plaintext

        # Encrypt: IV prepended to ciphertext (matches browser format)
        ciphertext = iv + aesgcm.encrypt(iv, envelope, None)

        tid = self.create_and_complete(ciphertext, content_type=content_type)

        # base64url key (no padding) — matches SendCrypto.exportKey
        key_b64 = base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode()
        return tid, key_b64
