"""Shared fixtures for v0.3.0 User UI acceptance tests.

Starts a real in-memory SG/Send API server and a UI static server
so Playwright tests run against a fully local stack — no network,
no S3, deterministic and fast.
"""

import pytest
import subprocess
import time
import os
import json
import base64
import httpx

from pathlib            import Path
from playwright.sync_api import sync_playwright

from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import (
    setup__send_user_lambda__test_server,
)


UI_PORT = 10062


# ---------------------------------------------------------------------------
# pytest markers
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line("markers", "p0: P0 — deployment blocker")
    config.addinivalue_line("markers", "p1: P1 — requires human sign-off if failing")
    config.addinivalue_line("markers", "p2: P2 — bug filed, does not block")
    config.addinivalue_line("markers", "p3: P3 — nice to have")


# ---------------------------------------------------------------------------
# API server (in-memory, session-scoped)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def send_server():
    """Start the real SG/Send User Lambda on a random port (in-memory storage).

    Yields test_objs with:
        .server_url     — e.g. http://127.0.0.1:54321
        .access_token   — pre-generated random GUID
        .write_key      — pre-generated random GUID
    """
    with setup__send_user_lambda__test_server() as test_objs:
        yield test_objs


@pytest.fixture(scope="session")
def api_url(send_server):
    """Base URL of the local API server."""
    return send_server.server_url


# ---------------------------------------------------------------------------
# UI static server (session-scoped)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def ui_server(send_server):
    """Start the UI static server pointing at the local API.

    Runs scripts/user__run-locally.sh with SGRAPH_API_ENDPOINT overridden
    to the local in-memory API server.  Waits up to 15 s for the UI to
    become reachable on localhost:{UI_PORT}.
    """
    script = Path("scripts/user__run-locally.sh")
    if not script.exists():
        pytest.skip("scripts/user__run-locally.sh not found — UI server unavailable")

    env = os.environ.copy()
    env["SGRAPH_API_ENDPOINT"] = send_server.server_url

    proc = subprocess.Popen(
        ["bash", str(script)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            r = httpx.get(f"http://localhost:{UI_PORT}/en-gb/", timeout=2)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError(f"UI server failed to start on port {UI_PORT}")

    yield f"http://localhost:{UI_PORT}"

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="session")
def ui_url(ui_server):
    """Base URL of the local UI server (alias for clarity)."""
    return ui_server


# ---------------------------------------------------------------------------
# Playwright browser + page
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Headless Chromium shared across the session."""
    browser = playwright_instance.chromium.launch(
        headless=True,
        args=["--font-render-hinting=none"],
    )
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def browser_context(browser, ui_server):
    """Shared browser context with base_url set to the local UI."""
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        base_url=ui_server,
    )
    yield context
    context.close()


@pytest.fixture
def page(browser_context):
    """Fresh page per test."""
    page = browser_context.new_page()
    yield page
    page.close()


# ---------------------------------------------------------------------------
# Screenshots (reuses the project convention)
# ---------------------------------------------------------------------------

def _cdp_screenshot(page, path):
    """Take screenshot via CDP, bypassing Playwright's font-wait logic."""
    cdp    = page.context.new_cdp_session(page)
    result = cdp.send("Page.captureScreenshot", {"format": "png"})
    cdp.detach()
    Path(path).write_bytes(base64.b64decode(result["data"]))


@pytest.fixture
def screenshots(request):
    """Screenshot capture fixture — saves PNGs + metadata JSON.

    Groups screenshots by **module** (use case), not by method.
    test__access_gate.py  → access_gate/screenshots/
    test__navigation.py   → navigation/screenshots/

    Multiple test methods in the same module accumulate into one
    _metadata.json (appended per method, not overwritten).
    """
    # Derive use-case name from module: test__access_gate → access_gate
    module_name = request.node.module.__name__.split(".")[-1]
    use_case    = module_name.replace("test__", "")
    method_name = request.node.name

    shots_dir = Path("sg_send_qa__site/pages/use-cases") / use_case / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    captured = []

    class ScreenshotCapture:
        def capture(self, page, name, description=""):
            path = shots_dir / f"{name}.png"
            _cdp_screenshot(page, str(path))
            captured.append({"name": name, "path": str(path), "description": description})

        @property
        def all(self):
            return captured

        def save_metadata(self):
            meta_path = shots_dir / "_metadata.json"

            # Load existing metadata (from prior test methods in same module)
            if meta_path.exists():
                existing = json.loads(meta_path.read_text())
            else:
                existing = {
                    "use_case"   : use_case,
                    "module"     : module_name,
                    "module_doc" : request.node.module.__doc__ or "",
                    "tests"      : [],
                    "screenshots": [],
                }

            # Append this test method's data
            existing["tests"].append({
                "method"      : method_name,
                "doc"         : request.node.obj.__doc__ or "",
                "screenshots" : [s["name"] for s in captured],
            })
            existing["screenshots"].extend(captured)

            meta_path.write_text(json.dumps(existing, indent=2))

    capture = ScreenshotCapture()
    yield capture
    capture.save_metadata()


# ---------------------------------------------------------------------------
# TransferHelper — create encrypted transfers via API (for download tests)
# ---------------------------------------------------------------------------

class TransferHelper:
    """Create real encrypted transfers via the API without a browser.

    Matches the browser's Web Crypto encryption exactly:
      - AES-256-GCM, 12-byte random IV prepended to ciphertext
      - SGMETA envelope: magic(7) + length(4) + JSON metadata + content
    """

    SGMETA_MAGIC = bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41, 0x00])  # "SGMETA\0"

    def __init__(self, api_url, access_token=None):
        self.api_url = api_url
        self.headers = {}
        if access_token:
            self.headers["x-sgraph-access-token"] = access_token

    def create_and_complete(self, payload: bytes, content_type="application/octet-stream"):
        """Create → upload → complete a transfer.  Returns transfer_id."""
        create_resp = httpx.post(
            f"{self.api_url}/api/transfers/create",
            json={"file_size_bytes": len(payload), "content_type_hint": content_type},
            headers=self.headers,
        )
        create_resp.raise_for_status()
        tid = create_resp.json()["transfer_id"]

        httpx.post(
            f"{self.api_url}/api/transfers/upload/{tid}",
            content=payload,
            headers={**self.headers, "content-type": "application/octet-stream"},
        ).raise_for_status()

        httpx.post(
            f"{self.api_url}/api/transfers/complete/{tid}",
            headers=self.headers,
        ).raise_for_status()

        return tid

    def upload_encrypted(self, plaintext: bytes, filename="test.txt"):
        """Encrypt client-side (matching browser Web Crypto), upload, return (transfer_id, base64url_key)."""
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

        tid = self.create_and_complete(ciphertext)

        # base64url key (no padding) — matches SendCrypto.exportKey
        key_b64 = base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode()
        return tid, key_b64


@pytest.fixture(scope="session")
def transfer_helper(send_server):
    """TransferHelper wired to the local API server."""
    return TransferHelper(send_server.server_url, send_server.access_token)
