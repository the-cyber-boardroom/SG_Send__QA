# todo: refactored here to avoid circular imports, but this logic needs a complete refactor

def chromium_executable_path():                                                         # resolve Chromium binary from playwright's own registry
    from sg_send_qa.browser import shared_playwright_state
    if shared_playwright_state.instance is not None:                                # reuse existing instance — avoids "inside asyncio loop" error
        return shared_playwright_state.instance.chromium.executable_path
    from playwright.sync_api import sync_playwright                                 # late import — avoids circular deps
    pw   = sync_playwright().start()
    path = pw.chromium.executable_path
    pw.stop()
    return path
