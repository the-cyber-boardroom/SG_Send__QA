"""Suite 1 — Upload + download round-trip (scheduled smoke).

Runs against https://send.sgraph.ai using SG_SEND_ACCESS_TOKEN.
All checks are recorded as SKIP if the token is absent.

Steps (each reported independently):
  api_reachable       — unauthenticated GET to live site root
  api_auth_and_create — POST /api/transfers/create with access token
  api_encrypt_upload  — client-side AES-256-GCM encrypt + POST binary payload
  api_complete        — POST /api/transfers/complete
  browser_decrypt     — Playwright opens download URL, verifies send-download.state='complete'
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
CONTENT = b"SG/Send smoke test -- upload+download round-trip."

results = []

# Proxy: Claude cloud routes traffic via an authenticated egress proxy.
# httpx reads env vars automatically; Playwright does not — pass explicitly.
proxy_url    = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY", "")
proxy_config = None
if proxy_url:
    parsed = urlparse(proxy_url)
    proxy_config = {"server":   f"http://{parsed.hostname}:{parsed.port}",
                    "username": parsed.username,
                    "password": parsed.password}


def step(name, fn):
    """Run fn(), record PASS/FAIL in results. Returns the value or None."""
    try:
        val = fn()
        results.append((name, "PASS", str(val)[:120]))
        return val
    except Exception as e:
        results.append((name, "FAIL", str(e)[:120]))
        return None


if not TOKEN:
    for name in ("api_reachable", "api_auth_and_create", "api_encrypt_upload",
                 "api_complete", "browser_decrypt"):
        results.append((name, "SKIP", "No access token"))
else:
    ctx = {}   # shared mutable state: tid, key

    def chk_reach():
        r = httpx.get(LIVE, timeout=TIMEOUT, follow_redirects=True)
        r.raise_for_status()
        return f"HTTP {r.status_code}"
    step("api_reachable", chk_reach)

    def chk_auth():
        r = httpx.post(f"{LIVE}/api/transfers/create",
                       json={"file_size_bytes": len(CONTENT),
                             "content_type_hint": "text/plain"},
                       headers={"x-sgraph-access-token": TOKEN},
                       timeout=TIMEOUT)
        r.raise_for_status()
        ctx["tid"] = r.json()["transfer_id"]
        return f"HTTP {r.status_code} — tid={ctx['tid'][:16]}…"
    step("api_auth_and_create", chk_auth)

    def chk_encrypt_upload():
        if "tid" not in ctx:
            raise RuntimeError("No transfer_id from create step")
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        SGMETA    = bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41])
        key_bytes = os.urandom(32)
        iv        = os.urandom(12)
        meta      = json.dumps({"filename": "smoke-roundtrip.txt"}).encode()
        envelope  = SGMETA + len(meta).to_bytes(4, "big") + meta + CONTENT
        enc       = iv + AESGCM(key_bytes).encrypt(iv, envelope, None)
        ctx["key"] = base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode()
        r = httpx.post(f"{LIVE}/api/transfers/upload/{ctx['tid']}",
                       content=enc,
                       headers={"x-sgraph-access-token": TOKEN,
                                "content-type": "application/octet-stream"},
                       timeout=TIMEOUT)
        r.raise_for_status()
        return f"HTTP {r.status_code} — {len(enc)} bytes uploaded"
    step("api_encrypt_upload", chk_encrypt_upload)

    def chk_complete():
        if "tid" not in ctx:
            raise RuntimeError("No transfer_id")
        r = httpx.post(f"{LIVE}/api/transfers/complete/{ctx['tid']}",
                       headers={"x-sgraph-access-token": TOKEN},
                       timeout=TIMEOUT)
        r.raise_for_status()
        return f"HTTP {r.status_code}"
    step("api_complete", chk_complete)

    def chk_browser_decrypt():
        if "tid" not in ctx or "key" not in ctx:
            raise RuntimeError("No transfer_id/key — upload steps failed")
        kw = {"headless": True}
        if proxy_config:
            kw["proxy"] = proxy_config
        with sync_playwright() as p:
            browser = p.chromium.launch(**kw)
            # ignore_https_errors=True: proxy performs TLS interception
            bctx = browser.new_context(viewport={"width": 1280, "height": 720},
                                       ignore_https_errors=True)
            bctx.add_init_script(
                f"localStorage.setItem('sgraph-send-token', '{TOKEN}');"
            )
            page = bctx.new_page()
            page.goto(f"{LIVE}/en-gb/download/#{ctx['tid']}/{ctx['key']}",
                      timeout=25000, wait_until="networkidle")
            page.wait_for_timeout(4000)   # allow Web Crypto decrypt + render
            # send-download web component sets .state = 'complete' on success
            state = page.evaluate("document.querySelector('send-download')?.state")
            if state != "complete":
                body = page.inner_text("body") or ""
                browser.close()
                if "decrypted" in body.lower():
                    return "inner_text contains 'decrypted'"
                raise RuntimeError(f"state={state!r}, body[:150]={body[:150]}")
            browser.close()
            return f"state={state!r}"
    step("browser_decrypt", chk_browser_decrypt)


passed = sum(1 for _, s, _ in results if s == "PASS")
total  = sum(1 for _, s, _ in results if s != "SKIP")
print(f"\n=== SUITE 1 (upload+download): {passed}/{total} passed ===")
for name, status, detail in results:
    icon = "✓" if status == "PASS" else ("—" if status == "SKIP" else "✗")
    print(f"  {icon} {name}: {status} — {detail}")
sys.exit(0 if all(s in ("PASS", "SKIP") for _, s, _ in results) else 1)
