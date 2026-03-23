"""Root conftest — Playwright setup for production-targeted integration tests.

Thin wrapper: all implementation lives in sg_send_qa/.
"""

import os
import urllib.request

import pytest
from playwright.sync_api import sync_playwright

from sg_send_qa.utils.QA_Screenshot_Capture import ScreenshotCapture


def _check_target_reachable(url: str) -> bool:
    """Return True if url responds within 5 s (False in sandboxed environments)."""
    try:
        urllib.request.urlopen(url, timeout=5)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--font-render-hinting=none"],
        )
        yield browser
        browser.close()


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
