"""CDP-based screenshot capture for SG/Send QA.

Provides the single canonical _cdp_screenshot implementation.
Previously copy-pasted 4 times (root conftest, v030 conftest,
standalone conftest, bugs test). This is the ONE copy.

Usage:
    from sg_send_qa.utils.QA_Screenshot import cdp_screenshot
    cdp_screenshot(page, "path/to/output.png")
"""

import base64
from pathlib import Path


def cdp_screenshot(page, path: str) -> None:
    """Take a screenshot via CDP, bypassing Playwright's font-wait logic.

    Playwright's built-in screenshot waits for fonts to load, which can
    cause flakiness and slow down CI. CDP captures the frame immediately.

    Args:
        page: Playwright Page object.
        path: Filesystem path for the output PNG (created if missing).
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    cdp    = page.context.new_cdp_session(page)
    result = cdp.send("Page.captureScreenshot", {"format": "png"})
    cdp.detach()
    Path(path).write_bytes(base64.b64decode(result["data"]))
