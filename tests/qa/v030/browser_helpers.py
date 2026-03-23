"""Shared browser helpers for v0.3.0 Playwright tests."""


def goto(page, url: str) -> None:
    """Navigate and wait for DOM ready.

    Uses domcontentloaded instead of networkidle — the SG/Send UI makes
    background API calls (health checks, token validation) that prevent
    networkidle from ever resolving, causing 30s timeouts per call.
    """
    page.goto(url, wait_until="domcontentloaded")


def handle_access_gate(page, access_token: str) -> None:
    """Submit the access gate if it is visible.

    The access gate shadow DOM renders in this button order:
      1. #toggle-token-vis  — eye icon (show/hide password) ← NOT this one
      2. #access-token-submit — 'Go' button                ← this one

    page.locator("button").first.click() hits the eye icon by mistake.
    Always target #access-token-submit explicitly.
    """
    gate_input = page.locator("#access-token-input")
    if gate_input.is_visible(timeout=2000):
        gate_input.fill(access_token)
        page.locator("#access-token-submit").click()
        page.wait_for_timeout(500)
