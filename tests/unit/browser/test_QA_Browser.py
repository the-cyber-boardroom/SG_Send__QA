# ═══════════════════════════════════════════════════════════════════════════════
# Tests for QA_Browser — persistent browser wrapper
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                       import TestCase
from osbot_utils.utils.Files                                                                        import file_exists
from sg_send_qa.browser.QA_Browser                                                                  import QA_Browser, DEFAULT_BROWSER_PORT, DEFAULT_HEADLESS
from sg_send_qa.browser.for__osbot_playwright.SG_Send__Playwright_Browser__Chrome                   import chromium_executable_path


class test_QA_Browser(TestCase):                                                # Unit tests — no browser needed

    def test_chromium_executable_path(self):                                    # finds the playwright-installed Chromium
        path = chromium_executable_path()
        assert 'chrom' in path.lower()
        assert file_exists(path)

    def test__init__(self):                                                     # verify default attribute values
        with QA_Browser() as _:
            assert type(_)    is QA_Browser
            assert _.port     == DEFAULT_BROWSER_PORT
            assert _.headless == DEFAULT_HEADLESS

    def test__init____with_overrides(self):                                     # verify constructor accepts overrides
        with QA_Browser(port=9999, headless=True) as _:
            assert _.port     == 9999
            assert _.headless is True

    def test_healthy__before_start(self):                                       # healthy is False before chrome() called
        with QA_Browser(port=19999) as _:                                       # use unique port to avoid hitting a running instance
            assert _.healthy() is False