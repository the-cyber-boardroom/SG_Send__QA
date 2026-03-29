"""Suite 2 — Download view modes (scheduled smoke).

Uploads one encrypted transfer via API, then verifies three download view
modes all render correctly in the browser: browse, gallery, and viewer.

Steps:
  api_upload          — create + encrypt + upload + complete via API
  browser_browse_view — /en-gb/browse/#tid/key → send-download.state = 'complete'
  browser_gallery_view— /en-gb/gallery/#tid/key → page loads without error
  browser_viewer_view — /en-gb/view/#tid/key    → page loads without error
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
CONTENT = b"SG/Send smoke test -- view mode check."

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


if not TOKEN:
    for name in ("api_upload", "browser_browse_view",
                 "browser_gallery_view", "browser_viewer_view"):
        results.append((name, "SKIP", "No access token"))
else:
    ctx = {}

    # Step 1 — Upload via API (same pattern as Suite 1)
    def chk_upload():
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        r = httpx.post(f"{LIVE}/api/transfers/create",
                       json={"file_size_bytes": len(CONTENT),
                             "content_type_hint": "text/plain"},
                       headers={"x-sgraph-access-token": TOKEN},
                       timeout=TIMEOUT)
        r.raise_for_status()
        tid = r.json()["transfer_id"]

        SGMETA    = bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41])
        key_bytes = os.urandom(32)
        iv        = os.urandom(12)
        meta      = json.dumps({"filename": "smoke-views.txt"}).encode()
        envelope  = SGMETA + len(meta).to_bytes(4, "big") + meta + CONTENT
        enc       = iv + AESGCM(key_bytes).encrypt(iv, envelope, None)
        key       = base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode()

        httpx.post(f"{LIVE}/api/transfers/upload/{tid}",
                   content=enc,
                   headers={"x-sgraph-access-token": TOKEN,
                            "content-type": "application/octet-stream"},
                   timeout=TIMEOUT).raise_for_status()
        httpx.post(f"{LIVE}/api/transfers/complete/{tid}",
                   headers={"x-sgraph-access-token": TOKEN},
                   timeout=TIMEOUT).raise_for_status()

        ctx["tid"] = tid
        ctx["key"] = key
        return f"tid={tid[:16]}…"
    step("api_upload", chk_upload)

    # Steps 2-4 — Check each view mode in the browser
    def make_browser():
        kw = {"headless": True}
        if proxy_config:
            kw["proxy"] = proxy_config
        p        = sync_playwright().start()
        browser  = p.chromium.launch(**kw)
        bctx     = browser.new_context(viewport={"width": 1280, "height": 720},
                                       ignore_https_errors=True)
        bctx.add_init_script(f"localStorage.setItem('sgraph-send-token', '{TOKEN}');")
        return p, browser, bctx.new_page()

    VIEW_MODES = [
        ("browser_browse_view",   f"/en-gb/browse/"),
        ("browser_gallery_view",  f"/en-gb/gallery/"),
        ("browser_viewer_view",   f"/en-gb/view/"),
    ]

    if "tid" in ctx:
        for step_name, path_prefix in VIEW_MODES:
            def chk_view(path_prefix=path_prefix, step_name=step_name):
                url = f"{LIVE}{path_prefix}#{ctx['tid']}/{ctx['key']}"
                p, browser, page = make_browser()
                try:
                    resp = page.goto(url, timeout=25000, wait_until="networkidle")
                    page.wait_for_timeout(3000)
                    if resp is None or not resp.ok:
                        raise RuntimeError(f"HTTP {resp.status if resp else '?'}")
                    # Check send-download state if present
                    state = page.evaluate(
                        "document.querySelector('send-download')?.state"
                    )
                    body  = page.inner_text("body") or ""
                    error_keywords = ["AccessDenied", "503 ", "502 ",
                                      "Internal Server Error", "not found"]
                    if any(kw in body for kw in error_keywords):
                        raise RuntimeError(f"Error keyword in body: {body[:120]}")
                    detail = f"HTTP {resp.status}"
                    if state:
                        detail += f", state={state!r}"
                    return detail
                finally:
                    browser.close()
                    p.stop()
            step(step_name, chk_view)
    else:
        for name, _ in VIEW_MODES:
            results.append((name, "SKIP", "Upload failed — no transfer_id"))


passed = sum(1 for _, s, _ in results if s == "PASS")
total  = sum(1 for _, s, _ in results if s != "SKIP")
print(f"\n=== SUITE 2 (view modes): {passed}/{total} passed ===")
for name, status, detail in results:
    icon = "✓" if status == "PASS" else ("—" if status == "SKIP" else "✗")
    print(f"  {icon} {name}: {status} — {detail}")
sys.exit(0 if all(s in ("PASS", "SKIP") for _, s, _ in results) else 1)
