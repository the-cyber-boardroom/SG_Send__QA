"""Suite 3 — Error states (scheduled smoke).

Verifies that invalid inputs produce a clean error in the browser
(send-download.state='error'), not a crash or unexpected state.

Steps:
  error_wrong_key  — API upload → navigate with a different random key
                     → send-download.state should be 'error'
  error_bogus_hash — navigate with a completely fabricated hash
                     → send-download.state should be 'error', no server crash
"""

import os
import sys
import json
import base64
import httpx
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

LIVE    = "https://send.sgraph.ai"
TOKEN   = os.environ.get("SG_SEND_ACCESS_TOKEN", "")
TIMEOUT = 30.0

results = []

proxy_url    = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY", "")
proxy_config = None
if proxy_url:
    parsed = urlparse(proxy_url)
    proxy_config = {"server":   f"http://{parsed.hostname}:{parsed.port}",
                    "username": parsed.username,
                    "password": parsed.password}


def step(name, fn):
    try:
        val = fn()
        results.append((name, "PASS", str(val)[:120]))
        return val
    except Exception as e:
        results.append((name, "FAIL", str(e)[:120]))
        return None


def wait_for_download_states(page, states, timeout=15000):
    """Wait for send-download.state to reach one of the given states."""
    vals_js = "[" + ", ".join(f'"{s}"' for s in states) + "]"
    pred    = (f'() => {{ var el = document.querySelector("send-download"); '
               f'if (!el) return false; '
               f'return {vals_js}.indexOf(el.state) !== -1 }}')
    page.wait_for_function(pred, timeout=timeout)


def open_browser():
    kw = {"headless": True}
    if proxy_config:
        kw["proxy"] = proxy_config
    return kw


if not TOKEN:
    for name in ("error_wrong_key", "error_bogus_hash"):
        results.append((name, "SKIP", "No access token"))
else:
    def chk_wrong_key():
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        # 1. Upload real content with a real key
        r = httpx.post(f"{LIVE}/api/transfers/create",
                       json={"file_size_bytes": 64, "content_type_hint": "text/plain"},
                       headers={"x-sgraph-access-token": TOKEN},
                       timeout=TIMEOUT)
        r.raise_for_status()
        tid = r.json()["transfer_id"]

        SGMETA    = bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41])
        key_bytes = os.urandom(32)
        iv        = os.urandom(12)
        content   = b"error-state test"
        meta      = json.dumps({"filename": "error-test.txt"}).encode()
        envelope  = SGMETA + len(meta).to_bytes(4, "big") + meta + content
        enc       = iv + AESGCM(key_bytes).encrypt(iv, envelope, None)

        httpx.post(f"{LIVE}/api/transfers/upload/{tid}",
                   content=enc,
                   headers={"x-sgraph-access-token": TOKEN,
                            "content-type": "application/octet-stream"},
                   timeout=TIMEOUT).raise_for_status()
        httpx.post(f"{LIVE}/api/transfers/complete/{tid}",
                   headers={"x-sgraph-access-token": TOKEN},
                   timeout=TIMEOUT).raise_for_status()

        # 2. Navigate with a DIFFERENT (wrong) key — decryption must fail
        wrong_key = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()
        url = f"{LIVE}/en-gb/browse/#{tid}/{wrong_key}"

        with sync_playwright() as p:
            browser = p.chromium.launch(**open_browser())
            bctx    = browser.new_context(viewport={"width": 1280, "height": 720},
                                          ignore_https_errors=True)
            bctx.add_init_script(f"localStorage.setItem('sgraph-send-token', '{TOKEN}');")
            page = bctx.new_page()
            resp = page.goto(url, timeout=25000, wait_until="networkidle")
            if resp is None or not resp.ok:
                browser.close()
                raise RuntimeError(f"HTTP {resp.status if resp else '?'}")
            wait_for_download_states(page, ["complete", "error"])
            state = page.evaluate("document.querySelector('send-download')?.state")
            browser.close()

        if state != "error":
            raise RuntimeError(f"Expected state='error' for wrong key, got {state!r}")
        return f"state={state!r} (correct — wrong key rejected)"
    step("error_wrong_key", chk_wrong_key)

    def chk_bogus_hash():
        # Completely fabricated transfer ID — server returns 404, component should reach 'error'
        bogus_tid = "totally-fake-transfer-id-00000000"
        bogus_key = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()
        url = f"{LIVE}/en-gb/browse/#{bogus_tid}/{bogus_key}"

        with sync_playwright() as p:
            browser = p.chromium.launch(**open_browser())
            bctx    = browser.new_context(viewport={"width": 1280, "height": 720},
                                          ignore_https_errors=True)
            bctx.add_init_script(f"localStorage.setItem('sgraph-send-token', '{TOKEN}');")
            page = bctx.new_page()
            resp = page.goto(url, timeout=25000, wait_until="networkidle")
            if resp is None or not resp.ok:
                browser.close()
                raise RuntimeError(f"HTTP {resp.status if resp else '?'}")
            wait_for_download_states(page, ["complete", "error"])
            state = page.evaluate("document.querySelector('send-download')?.state")
            body  = page.inner_text("body") or ""
            browser.close()

        crash_keywords = ["500 ", "502 ", "503 ", "Internal Server Error", "Traceback"]
        if any(kw in body for kw in crash_keywords):
            raise RuntimeError(f"Server error in body: {body[:120]}")
        if state != "error":
            raise RuntimeError(f"Expected state='error' for bogus hash, got {state!r}")
        return f"state={state!r} (correct — bogus hash rejected)"
    step("error_bogus_hash", chk_bogus_hash)


passed = sum(1 for _, s, _ in results if s == "PASS")
total  = sum(1 for _, s, _ in results if s != "SKIP")
print(f"\n=== SUITE 3 (error states): {passed}/{total} passed ===")
for name, status, detail in results:
    icon = "✓" if status == "PASS" else ("—" if status == "SKIP" else "✗")
    print(f"  {icon} {name}: {status} — {detail}")
sys.exit(0 if all(s in ("PASS", "SKIP") for _, s, _ in results) else 1)
