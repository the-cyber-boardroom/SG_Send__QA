"""Root conftest — Playwright setup shared across all test suites.

Single session-scoped playwright_instance prevents "Event loop is closed" /
"inside asyncio loop" errors that occur when multiple suites each create their
own sync_playwright() context in the same pytest session.
"""

import os
import urllib.request

import pytest
from playwright.sync_api import sync_playwright

from sg_send_qa.browser import shared_playwright_state
from sg_send_qa.utils.QA_Screenshot_Capture import ScreenshotCapture


def _check_target_reachable(url: str) -> bool:
    """Return True if url responds within 5 s (False in sandboxed environments)."""
    try:
        urllib.request.urlopen(url, timeout=5)
        return True
    except Exception:
        return False


# ─── Single session-scoped Playwright instance for the entire test run ────────
# All sub-conftest files (tests/qa/v030/, tests/qa/v031/, tests/smoke/) share
# this one instance.  Having multiple sync_playwright() contexts in the same
# session causes "Event loop is closed" / "inside asyncio loop" errors.

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        shared_playwright_state.instance = p      # expose to SG_Send__Playwright_Browser__Chrome
        yield p
        shared_playwright_state.instance = None   # clear on session teardown


@pytest.fixture(scope="session")
def browser(playwright_instance):
    b = playwright_instance.chromium.launch(
        headless=True,
        args=["--font-render-hinting=none"],
    )
    yield b
    b.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    page    = context.new_page()
    yield page
    context.close()


@pytest.fixture
def target_url():
    return os.environ.get("TEST_TARGET_URL", "https://send.sgraph.ai")


@pytest.fixture(autouse=True)
def skip_if_unreachable(request, target_url):
    """Skip browser tests if the target URL is unreachable (sandboxed env)."""
    if "integration" in str(request.fspath):
        if not _check_target_reachable(target_url):
            pytest.skip(f"Target {target_url} is unreachable (sandboxed environment)")


@pytest.fixture
def screenshots(request):
    """Screenshot capture fixture for production-targeted tests."""
    capture = ScreenshotCapture.from_request(request, test_target="production")
    yield capture
    capture.save_metadata()
