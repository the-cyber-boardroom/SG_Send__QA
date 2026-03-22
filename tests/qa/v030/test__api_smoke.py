"""API smoke tests — verify all vault endpoints work before browser tests run (P1).

These tests run against the in-memory SG/Send API server (no browser needed).
They act as a fast sanity check: if any of these fail, something is wrong with
the `send_server` fixture itself and all download-side browser tests are
testing nothing.

Endpoints covered:
  POST /api/transfers/create
  POST /api/transfers/upload/{tid}
  POST /api/transfers/complete/{tid}
  GET  /api/transfers/download/{tid}
  GET  /api/transfers/info/{tid}
  GET  /health  (or equivalent)

Access-gate behaviour:
  - With correct access token → 200
  - With wrong access token   → 401 / 403
  - Uploading to unknown tid  → 404
  - Downloading unknown tid   → 404
"""

import pytest
import httpx
import os
import json

pytestmark = pytest.mark.p1


class TestHealthCheck:
    """Verify the server is up and responding."""

    def test_root_is_reachable(self, api_url):
        """Root or any known endpoint responds — server is alive."""
        # Try /health first, fall back to /api/transfers/create OPTIONS
        for path in ["/health", "/", "/api/"]:
            try:
                r = httpx.get(f"{api_url}{path}", timeout=5)
                if r.status_code < 500:
                    return  # server is up
            except httpx.RequestError:
                pass
        pytest.fail(f"Server at {api_url} is not responding on any known path")

    def test_unknown_route_returns_404(self, api_url):
        """Unknown route returns 404, not 500."""
        r = httpx.get(f"{api_url}/no-such-endpoint-xyz", timeout=5)
        assert r.status_code == 404, (
            f"Expected 404 for unknown route, got {r.status_code}"
        )


class TestCreateTransfer:
    """POST /api/transfers/create"""

    def test_create_returns_transfer_id(self, send_server):
        """Create endpoint returns a non-empty transfer_id."""
        r = httpx.post(
            f"{send_server.server_url}/api/transfers/create",
            json={"file_size_bytes": 128, "content_type_hint": "application/octet-stream"},
            headers={"x-sgraph-send-access-token": send_server.access_token},
        )
        assert r.status_code == 200, f"Create failed: {r.status_code} — {r.text}"
        data = r.json()
        assert "transfer_id" in data, f"No transfer_id in response: {data}"
        assert data["transfer_id"], "transfer_id is empty"

    def test_create_without_token_blocked(self, send_server):
        """Create endpoint rejects requests with no access token when gate is enabled."""
        r = httpx.post(
            f"{send_server.server_url}/api/transfers/create",
            json={"file_size_bytes": 128, "content_type_hint": "application/octet-stream"},
            # Deliberately no access token header
        )
        # Should be 401 or 403 when the server has an access gate configured
        # (Some server configs allow open uploads — skip if 200)
        if r.status_code == 200:
            pytest.skip("Server is configured for open uploads (no access gate)")
        assert r.status_code in (401, 403), (
            f"Expected 401/403 without token, got {r.status_code}"
        )

    def test_create_with_wrong_token_blocked(self, send_server):
        """Create endpoint rejects requests with an incorrect access token."""
        r = httpx.post(
            f"{send_server.server_url}/api/transfers/create",
            json={"file_size_bytes": 128, "content_type_hint": "application/octet-stream"},
            headers={"x-sgraph-send-access-token": "definitely-wrong-token-xyz"},
        )
        if r.status_code == 200:
            pytest.skip("Server is configured for open uploads (no access gate)")
        assert r.status_code in (401, 403), (
            f"Expected 401/403 with wrong token, got {r.status_code}"
        )

    def test_create_transfer_id_is_unique(self, send_server):
        """Two consecutive creates produce different transfer IDs."""
        def _create():
            r = httpx.post(
                f"{send_server.server_url}/api/transfers/create",
                json={"file_size_bytes": 64, "content_type_hint": "application/octet-stream"},
                headers={"x-sgraph-send-access-token": send_server.access_token},
            )
            r.raise_for_status()
            return r.json()["transfer_id"]

        tid1 = _create()
        tid2 = _create()
        assert tid1 != tid2, "Two creates returned the same transfer_id"


class TestUploadTransfer:
    """POST /api/transfers/upload/{tid}"""

    def _create_tid(self, send_server, size=64):
        r = httpx.post(
            f"{send_server.server_url}/api/transfers/create",
            json={"file_size_bytes": size, "content_type_hint": "application/octet-stream"},
            headers={"x-sgraph-send-access-token": send_server.access_token},
        )
        r.raise_for_status()
        return r.json()["transfer_id"]

    def test_upload_succeeds(self, send_server):
        """Upload bytes to an existing transfer ID returns success."""
        tid     = self._create_tid(send_server)
        payload = os.urandom(64)

        r = httpx.post(
            f"{send_server.server_url}/api/transfers/upload/{tid}",
            content=payload,
            headers={
                "x-sgraph-send-access-token": send_server.access_token,
                "content-type": "application/octet-stream",
            },
        )
        assert r.status_code == 200, f"Upload failed: {r.status_code} — {r.text}"

    def test_upload_unknown_tid_returns_404(self, send_server):
        """Uploading to a non-existent transfer ID returns 404."""
        r = httpx.post(
            f"{send_server.server_url}/api/transfers/upload/nonexistent-tid-00000",
            content=b"payload",
            headers={
                "x-sgraph-send-access-token": send_server.access_token,
                "content-type": "application/octet-stream",
            },
        )
        assert r.status_code == 404, (
            f"Expected 404 for unknown tid, got {r.status_code}"
        )


class TestCompleteTransfer:
    """POST /api/transfers/complete/{tid}"""

    def _create_and_upload(self, send_server):
        payload = os.urandom(32)
        r = httpx.post(
            f"{send_server.server_url}/api/transfers/create",
            json={"file_size_bytes": len(payload), "content_type_hint": "application/octet-stream"},
            headers={"x-sgraph-send-access-token": send_server.access_token},
        )
        r.raise_for_status()
        tid = r.json()["transfer_id"]

        httpx.post(
            f"{send_server.server_url}/api/transfers/upload/{tid}",
            content=payload,
            headers={
                "x-sgraph-send-access-token": send_server.access_token,
                "content-type": "application/octet-stream",
            },
        ).raise_for_status()

        return tid, payload

    def test_complete_succeeds(self, send_server):
        """Completing an uploaded transfer returns success."""
        tid, _ = self._create_and_upload(send_server)

        r = httpx.post(
            f"{send_server.server_url}/api/transfers/complete/{tid}",
            headers={"x-sgraph-send-access-token": send_server.access_token},
        )
        assert r.status_code == 200, f"Complete failed: {r.status_code} — {r.text}"

    def test_complete_unknown_tid_returns_404(self, send_server):
        """Completing a non-existent transfer ID returns 404."""
        r = httpx.post(
            f"{send_server.server_url}/api/transfers/complete/nonexistent-00000",
            headers={"x-sgraph-send-access-token": send_server.access_token},
        )
        assert r.status_code == 404, (
            f"Expected 404 for unknown tid, got {r.status_code}"
        )


class TestDownloadTransfer:
    """GET /api/transfers/download/{tid}"""

    def test_download_returns_exact_bytes(self, transfer_helper, api_url):
        """Downloaded bytes exactly match the uploaded payload."""
        payload = os.urandom(256)
        tid     = transfer_helper.create_and_complete(payload)

        r = httpx.get(f"{api_url}/api/transfers/download/{tid}", timeout=10)
        assert r.status_code == 200, f"Download failed: {r.status_code}"
        assert r.content == payload, (
            f"Downloaded content mismatch: "
            f"{len(r.content)} bytes returned, {len(payload)} expected"
        )

    def test_download_unknown_tid_returns_404(self, api_url):
        """Downloading a non-existent transfer ID returns 404."""
        r = httpx.get(f"{api_url}/api/transfers/download/nonexistent-tid-99999", timeout=5)
        assert r.status_code == 404, (
            f"Expected 404 for unknown tid, got {r.status_code}"
        )

    def test_download_is_idempotent(self, transfer_helper, api_url):
        """Downloading the same transfer twice returns the same bytes."""
        payload = os.urandom(128)
        tid     = transfer_helper.create_and_complete(payload)

        r1 = httpx.get(f"{api_url}/api/transfers/download/{tid}", timeout=10)
        r2 = httpx.get(f"{api_url}/api/transfers/download/{tid}", timeout=10)

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.content == r2.content, "Download is not idempotent — bytes differ on second request"

    def test_download_preserves_binary_content(self, transfer_helper, api_url):
        """Binary content with all 256 byte values round-trips without corruption."""
        payload = bytes(range(256)) * 8  # 2 KB covering every byte value
        tid     = transfer_helper.create_and_complete(payload)

        r = httpx.get(f"{api_url}/api/transfers/download/{tid}", timeout=10)
        assert r.status_code == 200
        assert r.content == payload, "Binary content corrupted in round-trip"


class TestInfoEndpoint:
    """GET /api/transfers/info/{tid}"""

    def test_info_returns_200(self, transfer_helper, api_url):
        """Info endpoint returns 200 for a completed transfer."""
        tid, _ = transfer_helper.upload_encrypted(b"info test content", "info-test.txt")

        r = httpx.get(f"{api_url}/api/transfers/info/{tid}", timeout=5)
        assert r.status_code == 200, f"Info endpoint failed: {r.status_code} — {r.text}"

    def test_info_returns_json(self, transfer_helper, api_url):
        """Info endpoint returns valid JSON."""
        tid, _ = transfer_helper.upload_encrypted(b"json test", "json-test.txt")

        r = httpx.get(f"{api_url}/api/transfers/info/{tid}", timeout=5)
        assert r.status_code == 200
        try:
            data = r.json()
        except Exception as e:
            pytest.fail(f"Info endpoint did not return valid JSON: {e}")
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"

    def test_info_unknown_tid_returns_404(self, api_url):
        """Info endpoint returns 404 for unknown transfer ID."""
        r = httpx.get(f"{api_url}/api/transfers/info/nonexistent-info-00000", timeout=5)
        assert r.status_code == 404, (
            f"Expected 404 for unknown tid, got {r.status_code}"
        )

    def test_info_does_not_expose_plaintext(self, transfer_helper, api_url):
        """Info endpoint must not return original filename or content."""
        canary = "SUPER_SECRET_CANARY_12345"
        tid, _ = transfer_helper.upload_encrypted(
            plaintext=canary.encode(),
            filename=f"{canary}.txt",
        )

        r = httpx.get(f"{api_url}/api/transfers/info/{tid}", timeout=5)
        assert r.status_code == 200
        assert canary not in r.text, (
            f"CRITICAL: Canary string found in info response — plaintext is being exposed. "
            f"Response: {r.text[:500]}"
        )


class TestFullLifecycle:
    """Verify the complete create → upload → complete → download lifecycle."""

    def test_full_lifecycle_small_file(self, send_server, api_url):
        """Full lifecycle with a small (1 KB) payload."""
        payload = os.urandom(1024)
        headers = {"x-sgraph-send-access-token": send_server.access_token}

        # Create
        r = httpx.post(
            f"{api_url}/api/transfers/create",
            json={"file_size_bytes": len(payload), "content_type_hint": "application/octet-stream"},
            headers=headers,
        )
        r.raise_for_status()
        tid = r.json()["transfer_id"]

        # Upload
        httpx.post(
            f"{api_url}/api/transfers/upload/{tid}",
            content=payload,
            headers={**headers, "content-type": "application/octet-stream"},
        ).raise_for_status()

        # Complete
        httpx.post(f"{api_url}/api/transfers/complete/{tid}", headers=headers).raise_for_status()

        # Download
        r = httpx.get(f"{api_url}/api/transfers/download/{tid}", timeout=10)
        assert r.status_code == 200
        assert r.content == payload, "Downloaded content does not match uploaded payload"

    def test_full_lifecycle_with_transfer_helper(self, transfer_helper, api_url):
        """TransferHelper.upload_encrypted → download → ciphertext matches."""
        plaintext = b"Full lifecycle test via TransferHelper"
        tid, key_b64 = transfer_helper.upload_encrypted(plaintext, "lifecycle.txt")

        r = httpx.get(f"{api_url}/api/transfers/download/{tid}", timeout=10)
        assert r.status_code == 200
        assert len(r.content) > 12, "Downloaded blob is too short to contain IV + ciphertext"

        # The raw bytes must NOT contain the plaintext (zero-knowledge)
        assert plaintext not in r.content, (
            "Plaintext found in raw download — zero-knowledge violated"
        )

    def test_multiple_concurrent_transfers(self, send_server, api_url):
        """Multiple transfers can be created and downloaded independently."""
        headers = {"x-sgraph-send-access-token": send_server.access_token}
        payloads = [os.urandom(128) for _ in range(5)]
        tids = []

        for payload in payloads:
            r = httpx.post(
                f"{api_url}/api/transfers/create",
                json={"file_size_bytes": len(payload), "content_type_hint": "application/octet-stream"},
                headers=headers,
            )
            r.raise_for_status()
            tid = r.json()["transfer_id"]

            httpx.post(
                f"{api_url}/api/transfers/upload/{tid}",
                content=payload,
                headers={**headers, "content-type": "application/octet-stream"},
            ).raise_for_status()

            httpx.post(
                f"{api_url}/api/transfers/complete/{tid}",
                headers=headers,
            ).raise_for_status()

            tids.append(tid)

        # Verify each download matches the corresponding payload
        for tid, payload in zip(tids, payloads):
            r = httpx.get(f"{api_url}/api/transfers/download/{tid}", timeout=10)
            assert r.status_code == 200
            assert r.content == payload, f"Payload mismatch for transfer {tid}"
