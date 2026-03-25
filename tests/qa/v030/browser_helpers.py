"""Shared browser helpers for v0.3.0 Playwright tests."""

from sg_send_qa.browser.JS_Query__Execute import JS_Query__Execute


def _js(page):
    """Return a JS_Query__Execute wired to the given raw Playwright page."""
    return JS_Query__Execute(raw_page=page)


# ── Navigation ────────────────────────────────────────────────────────────────

def goto(page, url: str) -> None:
    """Navigate and wait for the SG/Send app to finish initialising.

    Uses wait_until="commit" (fires on first byte) — domcontentloaded is
    blocked by SG/Send inline scripts on some routes.  After the network
    commit, wait for body[data-ready] which the SG/Send bootstrap sets once
    the app shell is ready.
    """
    page.goto(url, wait_until="commit")
    page.wait_for_selector("body[data-ready]", timeout=10_000)


# ── Access gate ───────────────────────────────────────────────────────────────

def handle_access_gate(page, access_token: str) -> None:
    """Submit the access gate if it is visible.

    After clicking submit, wait for the gate to disappear (event-driven).
    The access gate shadow DOM renders buttons in this order:
      1. #toggle-token-vis  — eye icon (show/hide password) ← NOT this one
      2. #access-token-submit — 'Go' button                ← this one
    Always target #access-token-submit explicitly.
    """
    gate_input = page.locator("#access-token-input")
    if not gate_input.is_visible(timeout=2000):
        return

    gate_input.fill(access_token)
    page.locator("#access-token-submit").click()

    # Wait for gate to dismiss — either input disappears or upload wizard appears
    pred = _js(page).predicate__light_not_exists("#access-token-input")
    try:
        page.wait_for_function(pred, timeout=5000)
    except Exception:
        pass                                                                    # gate may already be gone


# ── Upload state waits ────────────────────────────────────────────────────────

def wait_for_upload_state(page, state: str, timeout: int = 10_000) -> None:
    """Wait until send-upload._state === state."""
    pred = _js(page).predicate__light_property_equals("send-upload", "_state", state)
    page.wait_for_function(pred, timeout=timeout)


def wait_for_upload_states(page, states: list, timeout: int = 10_000) -> None:
    """Wait until send-upload._state is any of the given states."""
    pred = _js(page).predicate__light_property_in("send-upload", "_state", states)
    page.wait_for_function(pred, timeout=timeout)


# ── Download state waits ──────────────────────────────────────────────────────

def wait_for_download_state(page, state: str, timeout: int = 15_000) -> None:
    """Wait until send-download.state === state."""
    pred = _js(page).predicate__light_property_equals("send-download", "state", state)
    page.wait_for_function(pred, timeout=timeout)


def wait_for_download_states(page, states: list, timeout: int = 15_000) -> None:
    """Wait until send-download.state is any of the given states."""
    pred = _js(page).predicate__light_property_in("send-download", "state", states)
    page.wait_for_function(pred, timeout=timeout)
