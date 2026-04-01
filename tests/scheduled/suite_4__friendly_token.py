"""Suite 4 — Friendly token flow (scheduled smoke).

Uploads a file through the browser wizard using Simple Token share mode,
captures the friendly token (word-word-NNNN format), then resolves it
via /en-gb/browse/#<token> and verifies decryption succeeds.

Steps:
  browser_upload_token_mode — full wizard: select file → token share mode → upload
                              → friendly token captured
  browser_resolve_token     — navigate to /en-gb/browse/#<token>
                              → send-download.state='complete'
"""

import os
import sys
import re
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

LIVE    = "https://send.sgraph.ai"
TOKEN   = os.environ.get("SG_SEND_ACCESS_TOKEN", "")
CONTENT = b"SG/Send friendly token smoke test."

TOKEN_PATTERN = re.compile(r"^[a-z]+-[a-z]+-\d{4}$")

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


def wait_for_upload_states(page, states, timeout=30000):
    """Wait for send-upload._state to reach one of the given states."""
    vals_js = "[" + ", ".join(f'"{s}"' for s in states) + "]"
    pred    = (f'() => {{ var el = document.querySelector("send-upload"); '
               f'if (!el) return false; '
               f'return {vals_js}.indexOf(el["_state"]) !== -1 }}')
    page.wait_for_function(pred, timeout=timeout)


def wait_for_download_states(page, states, timeout=20000):
    """Wait for send-download.state to reach one of the given states."""
    vals_js = "[" + ", ".join(f'"{s}"' for s in states) + "]"
    pred    = (f'() => {{ var el = document.querySelector("send-download"); '
               f'if (!el) return false; '
               f'return {vals_js}.indexOf(el.state) !== -1 }}')
    page.wait_for_function(pred, timeout=timeout)


def get_friendly_token(page):
    """Extract the friendly token from upload-step-done shadow DOM."""
    return page.evaluate("""
        (() => {
            var host = document.querySelector('upload-step-done');
            if (!host || !host.shadowRoot) return null;
            var el = host.shadowRoot.querySelector('#simple-token');
            return el ? el.innerText.trim() : null;
        })()
    """)


def open_browser():
    kw = {"headless": True}
    if proxy_config:
        kw["proxy"] = proxy_config
    return kw


if not TOKEN:
    for name in ("browser_upload_token_mode", "browser_resolve_token"):
        results.append((name, "SKIP", "No access token"))
else:
    ctx = {}

    def chk_upload():
        with sync_playwright() as p:
            browser = p.chromium.launch(**open_browser())
            bctx    = browser.new_context(viewport={"width": 1280, "height": 720},
                                          ignore_https_errors=True)
            # Set token before page load so the access gate is bypassed
            bctx.add_init_script(f"localStorage.setItem('sgraph-send-token', '{TOKEN}');")
            page = bctx.new_page()

            # Navigate to upload page and wait for app init
            resp = page.goto(f"{LIVE}/en-gb/", timeout=25000, wait_until="networkidle")
            if resp is None or not resp.ok:
                browser.close()
                raise RuntimeError(f"HTTP {resp.status if resp else '?'} loading upload page")
            page.wait_for_selector("body[data-ready]", timeout=10000)

            # Set file via shadow DOM input
            file_input = page.locator("upload-step-select #file-input")
            file_input.wait_for(state="attached", timeout=10000)
            file_input.set_input_files([{
                "name"    : "smoke-token.txt",
                "mimeType": "text/plain",
                "buffer"  : CONTENT,
            }])
            wait_for_upload_states(page, ["file-ready", "choosing-delivery", "choosing-share"])

            # Advance past any delivery step to the share step
            next_btn = page.locator("#upload-next-btn")
            next_btn.wait_for(state="visible", timeout=5000)
            next_btn.click()
            wait_for_upload_states(page, ["choosing-share"])

            # Select Simple Token share mode
            token_card = page.locator('upload-step-share [data-mode="token"]')
            token_card.wait_for(state="visible", timeout=5000)
            token_card.click()
            wait_for_upload_states(page, ["confirming"])

            # Confirm and start upload
            next_btn.wait_for(state="visible", timeout=5000)
            next_btn.click()
            wait_for_upload_states(page, ["complete"], timeout=30000)

            # Extract the friendly token
            friendly_token = get_friendly_token(page)
            browser.close()

        if not friendly_token:
            raise RuntimeError("No friendly token found in upload-step-done #simple-token")
        if not TOKEN_PATTERN.match(friendly_token):
            raise RuntimeError(f"Token does not match word-word-NNNN: {friendly_token!r}")
        ctx["friendly_token"] = friendly_token
        return f"token={friendly_token!r}"
    step("browser_upload_token_mode", chk_upload)

    if "friendly_token" in ctx:
        def chk_resolve():
            token = ctx["friendly_token"]
            url   = f"{LIVE}/en-gb/browse/#{token}"

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

            if state != "complete":
                raise RuntimeError(
                    f"Expected state='complete' for token={token!r}, got {state!r}")
            return f"token={token!r}, state={state!r}"
        step("browser_resolve_token", chk_resolve)
    else:
        results.append(("browser_resolve_token", "SKIP", "Upload step failed — no token"))


passed = sum(1 for _, s, _ in results if s == "PASS")
total  = sum(1 for _, s, _ in results if s != "SKIP")
print(f"\n=== SUITE 4 (friendly token): {passed}/{total} passed ===")
for name, status, detail in results:
    icon = "✓" if status == "PASS" else ("—" if status == "SKIP" else "✗")
    print(f"  {icon} {name}: {status} — {detail}")
sys.exit(0 if all(s in ("PASS", "SKIP") for _, s, _ in results) else 1)
