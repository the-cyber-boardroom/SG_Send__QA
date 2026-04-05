# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Page__Send_SGraph_Ai__Gallery
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                                      import TestCase
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from sg_send_qa.apis_for_sites.send_sgraph_ai.pages.Page__Send_SGraph_Ai__Gallery import Page__Send_SGraph_Ai__Gallery
from sg_send_qa.browser.Schema__Browser_Test_Config                                import Schema__Browser_Test_Config
from sg_send_qa.browser.Schema__Gallery_Page                                       import Schema__Gallery_Page


# ═══════════════════════════════════════════════════════════════════════════════
# Non-browser unit tests — run in CI without Chromium
# ═══════════════════════════════════════════════════════════════════════════════

class test_Page__Send_SGraph_Ai__Gallery__Unit(TestCase):
    """Unit tests for Page__Send_SGraph_Ai__Gallery — no browser required."""

    def test_instantiation(self):                                             # class can be constructed with no arguments
        page = Page__Send_SGraph_Ai__Gallery()
        assert page is not None

    def test_is_type_safe_subclass(self):                                     # must be a Type_Safe subclass (project convention)
        page = Page__Send_SGraph_Ai__Gallery()
        assert isinstance(page, Type_Safe)

    def test_config_defaults_to_headless_true(self):                         # CI safety: headless must default to True
        page = Page__Send_SGraph_Ai__Gallery()
        assert isinstance(page.config, Schema__Browser_Test_Config)
        assert page.config.headless is True

    def test_config_can_be_overridden_to_headless_false(self):               # debug path: caller can force visible browser
        config = Schema__Browser_Test_Config(headless=False)
        page   = Page__Send_SGraph_Ai__Gallery(config=config)
        assert page.config.headless is False

    def test_harness_is_none_before_setup(self):                             # harness must not be started until setup() is called
        page = Page__Send_SGraph_Ai__Gallery()
        assert page.harness is None

    def test_sg_send_is_none_before_setup(self):                             # sg_send (browser pages) must not exist until setup()
        page = Page__Send_SGraph_Ai__Gallery()
        assert page.sg_send is None

    def test_has_setup_method(self):                                         # setup() must be present and callable
        page = Page__Send_SGraph_Ai__Gallery()
        assert callable(getattr(page, 'setup', None))

    def test_has_gallery_view_method(self):                                  # gallery_view() must be present and callable
        page = Page__Send_SGraph_Ai__Gallery()
        assert callable(getattr(page, 'gallery_view', None))

    def test_has_extract_state_method(self):                                 # extract_state() must be present and callable
        page = Page__Send_SGraph_Ai__Gallery()
        assert callable(getattr(page, 'extract_state', None))

    def test_has_teardown_method(self):                                      # teardown() must be present and callable
        page = Page__Send_SGraph_Ai__Gallery()
        assert callable(getattr(page, 'teardown', None))

    def test_teardown_is_safe_when_harness_is_none(self):                    # teardown() must not raise if setup() was never called
        page = Page__Send_SGraph_Ai__Gallery()
        page.teardown()                                                       # should complete without error


# ═══════════════════════════════════════════════════════════════════════════════
# Browser integration tests — require Chromium; skip in headless CI
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.skip("requires browser — run manually")
class test_Page__Send_SGraph_Ai__Gallery__Integration(TestCase):
    """Integration tests for Page__Send_SGraph_Ai__Gallery — browser required.

    Run locally with:
        pytest tests/qa/apis_for_sites/send_sgraph_ai/pages/ -k Integration -s
    """

    @classmethod
    def setUpClass(cls):
        cls.page = Page__Send_SGraph_Ai__Gallery()
        cls.page.setup()

    @classmethod
    def tearDownClass(cls):
        cls.page.teardown()

    def test_setup_creates_harness_and_sg_send(self):                        # setup() must populate harness and sg_send
        assert self.page.harness is not None
        assert self.page.sg_send is not None

    def test_extract_state_returns_gallery_page(self):                       # extract_state() returns correct type
        state = self.page.extract_state()
        assert isinstance(state, Schema__Gallery_Page)
