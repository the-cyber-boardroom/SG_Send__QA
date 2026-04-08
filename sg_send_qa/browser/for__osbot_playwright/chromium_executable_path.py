# todo: refactored here to avoid circular imports, but this logic needs a complete refactor

def chromium_executable_path():                                                         # resolve Chromium binary from playwright's own registry
    from playwright.sync_api import sync_playwright                                 # late import — avoids circular deps
    pw   = sync_playwright().start()
    path = pw.chromium.executable_path
    pw.stop()
    return path
