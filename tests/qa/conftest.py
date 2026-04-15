# ═══════════════════════════════════════════════════════════════════════════════
# Shared QA conftest
#
# playwright_instance is provided by tests/conftest.py (session-scoped, shared
# across tests/qa/v030/, tests/qa/v031/, tests/smoke/, tests/integration/ to
# avoid "Event loop is closed" / "inside asyncio loop" errors when multiple
# test suites run in the same pytest session).
# ═══════════════════════════════════════════════════════════════════════════════
