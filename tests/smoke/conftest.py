"""Smoke test suite — configurable target: dev, main, or prod.

Target configuration (in priority order):
  1. --target CLI option
  2. SG_SEND_TARGET env var
  3. Default: "dev"

Upload auth configuration (in priority order):
  1. --access-token CLI option
  2. SG_SEND_ACCESS_TOKEN env var
  3. Default: None (upload tests are skipped)

Usage examples:
  # Run against dev (default):
  pytest tests/smoke/ -v

  # Run against pre-prod:
  pytest tests/smoke/ -v --target=main

  # Run against prod with upload auth:
  pytest tests/smoke/ -v --target=prod --access-token=<token>

  # Using env vars:
  SG_SEND_TARGET=main SG_SEND_ACCESS_TOKEN=<token> pytest tests/smoke/ -v
"""

import os

import pytest
from playwright.sync_api import sync_playwright

from sg_send_qa.utils.QA_Screenshot_Capture import ScreenshotCapture
from sg_send_qa.utils.QA_Transfer_Helper import QA_Transfer_Helper

# ── Target URL map ─────────────────────────────────────────────────────────────

_TARGETS = {
    "dev":  "https://dev.send.sgraph.ai",
    "main": "https://main.send.sgraph.ai",
    "prod": "https://send.sgraph.ai",
}


# ── pytest options ─────────────────────────────────────────────────────────────

def pytest_addoption(parser):
    parser.addoption(
        "--target",
        default=None,
        help=(
            "Smoke test target environment: dev, main, prod, "
            "or a full URL (default: $SG_SEND_TARGET or 'dev')"
        ),
    )
    parser.addoption(
        "--access-token",
        default=None,
        help="API access token for upload tests (default: $SG_SEND_ACCESS_TOKEN)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: smoke test against a live environment")
    config.addinivalue_line(
        "markers",
        "smoke_upload: smoke test requiring API upload auth (skipped if no token)",
    )


# ── Session fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def target(request):
    """Resolved base URL for the target environment."""
    raw = (
        request.config.getoption("--target")
        or os.environ.get("SG_SEND_TARGET")
        or "dev"
    )
    if raw in _TARGETS:
        return _TARGETS[raw]
    if raw.startswith("http"):
        return raw.rstrip("/")
    raise ValueError(
        f"Unknown target: {raw!r}. Use dev / main / prod or a full URL."
    )


@pytest.fixture(scope="session")
def target_name(request, target):
    """Short name for the target (dev/main/prod/custom) — used in screenshot paths."""
    return next((k for k, v in _TARGETS.items() if v == target), "custom")


@pytest.fixture(scope="session")
def ui_url(target):
    return target


@pytest.fixture(scope="session")
def api_url(target):
    return target


@pytest.fixture(scope="session")
def access_token(request):
    return (
        request.config.getoption("--access-token")
        or os.environ.get("SG_SEND_ACCESS_TOKEN")
    )


@pytest.fixture(scope="session")
def transfer_helper(api_url, access_token):
    """QA_Transfer_Helper against the live target API. None if no access token."""
    if not access_token:
        return None
    return QA_Transfer_Helper(api_url=api_url, access_token=access_token)


# ── Playwright ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    import os
    from urllib.parse import urlparse

    proxy_kwargs = {}
    proxy_env = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy_env:
        parsed = urlparse(proxy_env)
        proxy_kwargs["proxy"] = {
            "server": f"http://{parsed.hostname}:{parsed.port}",
            "username": parsed.username or "",
            "password": parsed.password or "",
        }

    b = playwright_instance.chromium.launch(
        headless=True,
        args=["--font-render-hinting=none"],
        **proxy_kwargs,
    )
    yield b
    b.close()


@pytest.fixture(scope="session")
def browser_context(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    ctx.set_default_timeout(15_000)
    # Navigation against live servers with CDN deps uses domcontentloaded
    # (not "load") to avoid waiting for third-party scripts that may be slow.
    # Individual tests call page.goto(..., wait_until="domcontentloaded").
    ctx.set_default_navigation_timeout(60_000)
    yield ctx
    ctx.close()


@pytest.fixture
def page(browser_context):
    p = browser_context.new_page()
    yield p
    p.close()


# ── Screenshots ────────────────────────────────────────────────────────────────

@pytest.fixture
def screenshots(request, target_name):
    capture = ScreenshotCapture.from_request(
        request, test_target=f"smoke_{target_name}"
    )
    yield capture
    capture.save_metadata()


# ── Upload-gated skip ──────────────────────────────────────────────────────────

@pytest.fixture
def require_upload(transfer_helper, target_name):
    """Skip the test if no access token is configured."""
    if transfer_helper is None:
        pytest.skip(
            f"No access token for {target_name!r} — set SG_SEND_ACCESS_TOKEN "
            "or pass --access-token to run upload smoke tests."
        )
    return transfer_helper
