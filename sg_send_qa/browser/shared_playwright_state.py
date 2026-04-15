# ═══════════════════════════════════════════════════════════════════════════════
# Shared Playwright instance registry
#
# When the tests/qa/conftest.py session-scoped playwright_instance fixture
# is active, it stores the running Playwright object here so that
# SG_Send__Playwright_Browser__Chrome can reuse it rather than calling
# sync_playwright().start() again (which would fail with "inside asyncio loop").
# ═══════════════════════════════════════════════════════════════════════════════

instance = None                                       # set by conftest.py playwright_instance fixture
