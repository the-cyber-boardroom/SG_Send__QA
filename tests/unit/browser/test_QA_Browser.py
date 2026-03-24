# ═══════════════════════════════════════════════════════════════════════════════
# Tests for QA_Browser — persistent browser wrapper
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                           import TestCase

from osbot_utils.utils.Files import file_exists

from sg_send_qa.browser.QA_Browser import chromium_path, QA_Browser, DEFAULT_BROWSER_PORT, DEFAULT_HEADLESS


class test_QA_Browser(TestCase):                                                # Unit tests — no browser needed

    def test_chromium_path(self):                                               # finds the playwright-installed Chromium
        path = chromium_path()
        assert 'chrom' in path.lower()                                          # chromium or chrome
        assert file_exists(path)

    def test__init__(self):                                                     # verify default attribute values
        with QA_Browser() as _:
            assert type(_)    is QA_Browser
            assert _.port     == DEFAULT_BROWSER_PORT
            assert _.headless == DEFAULT_HEADLESS
            assert _._chrome  is None                                           # lazy — not created yet
            assert _._page    is None                                           # lazy — not created yet

    def test__init____with_overrides(self):                                     # verify constructor accepts overrides
        with QA_Browser(port=9999, headless=True) as _:
            assert _.port     == 9999
            assert _.headless is True

    def test_healthy__before_start(self):                                       # healthy is False before browser starts
        with QA_Browser() as _:
            assert _.healthy() is False

    def test_stop__before_start(self):                                          # stop is safe to call before start
        with QA_Browser() as _:
            assert _.stop() is False
