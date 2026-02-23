import pytest
import os
import base64
import urllib.request
from pathlib            import Path
from playwright.sync_api import sync_playwright


def _check_target_reachable(url):
    """Check if the target URL is reachable (may be blocked by proxy in sandboxed environments)."""
    try:
        urllib.request.urlopen(url, timeout=5)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless = True,
            args     = ["--font-render-hinting=none"],
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
    """Skip browser tests if the target URL is unreachable (e.g., sandboxed environment)."""
    if "integration" in str(request.fspath):
        if not _check_target_reachable(target_url):
            pytest.skip(f"Target {target_url} is unreachable (sandboxed environment)")


def _cdp_screenshot(page, path):
    """Take screenshot via CDP, bypassing Playwright's font-wait logic."""
    cdp    = page.context.new_cdp_session(page)
    result = cdp.send("Page.captureScreenshot", {"format": "png"})
    cdp.detach()
    png_data = base64.b64decode(result["data"])
    Path(path).write_bytes(png_data)


@pytest.fixture
def screenshots(request):
    """Screenshot capture fixture with descriptions."""
    test_name = request.node.name.replace("test_", "")
    shots_dir = Path("screenshots") / test_name
    shots_dir.mkdir(parents=True, exist_ok=True)

    captured = []

    class ScreenshotCapture:
        def capture(self, page, name, description=""):
            path = shots_dir / f"{name}.png"
            _cdp_screenshot(page, str(path))
            captured.append({
                "name"       : name,
                "path"       : str(path),
                "description": description,
            })

        @property
        def all(self):
            return captured

    return ScreenshotCapture()
