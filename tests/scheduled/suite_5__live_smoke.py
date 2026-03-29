"""Suite 5 — Live site smoke (scheduled smoke).

Playwright HTTP checks against https://send.sgraph.ai.
Verifies all key routes return HTTP 200 through the egress proxy.

Notes:
- Playwright does not read https_proxy env vars automatically; proxy is passed
  explicitly to p.chromium.launch(proxy=...).
- ignore_https_errors=True is required: the egress proxy performs TLS interception.
- curl reads proxy env vars natively, so curl success with Playwright 407 means
  the proxy config is missing from the launch kwargs.
"""

import os
import sys
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

LIVE  = "https://send.sgraph.ai"
TOKEN = os.environ.get("SG_SEND_ACCESS_TOKEN", "")

results = []

proxy_url    = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY", "")
proxy_config = None
if proxy_url:
    parsed = urlparse(proxy_url)
    proxy_config = {"server":   f"http://{parsed.hostname}:{parsed.port}",
                    "username": parsed.username,
                    "password": parsed.password}
    print(f"Proxy: {parsed.hostname}:{parsed.port}")
else:
    print("No proxy configured")

if TOKEN:
    print(f"SG_SEND_ACCESS_TOKEN: set ({len(TOKEN)} chars)")
else:
    print("SG_SEND_ACCESS_TOKEN: NOT SET — upload tests will be skipped")

launch_kwargs = {"headless": True}
if proxy_config:
    launch_kwargs["proxy"] = proxy_config

with sync_playwright() as p:
    browser = p.chromium.launch(**launch_kwargs)
    ctx     = browser.new_context(viewport={"width": 1280, "height": 720},
                                  ignore_https_errors=True)
    if TOKEN:
        ctx.add_init_script(f"localStorage.setItem('sgraph-send-token', '{TOKEN}');")

    page = ctx.new_page()

    def check(name, url, extra_wait=2000):
        try:
            resp = page.goto(url, timeout=20000, wait_until="networkidle")
            page.wait_for_timeout(extra_wait)
            ok = resp is not None and resp.ok
            results.append((name, "PASS" if ok else "FAIL",
                            f"HTTP {resp.status if resp else '?'} · {page.url[:60]}"))
        except Exception as e:
            results.append((name, "FAIL", str(e)[:100]))

    check("root",           LIVE)
    check("download_entry", f"{LIVE}/en-gb/download/")
    check("gallery_route",  f"{LIVE}/en-gb/gallery/")
    check("browse_route",   f"{LIVE}/en-gb/browse/")
    check("viewer_route",   f"{LIVE}/en-gb/view/")
    check("invalid_hash",   f"{LIVE}/en-gb/download/#bogus123/fakekey==")

    browser.close()

passed = sum(1 for _, s, _ in results if s == "PASS")
print(f"\n=== LIVE SITE: {passed}/{len(results)} passed ===")
for name, status, detail in results:
    print(f"  {'✓' if status == 'PASS' else '✗'} {name}: {status} — {detail}")
sys.exit(0 if passed == len(results) else 1)
