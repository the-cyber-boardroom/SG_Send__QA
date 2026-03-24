# ═══════════════════════════════════════════════════════════════════════════════
# Tests for SG_Send__Browser__Test_Harness
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                          import Schema__Browser_Test_Config


class test_Schema__Browser_Test_Config(TestCase):                               # Unit tests — no servers needed

    def test__init__(self):                                                     # verify defaults
        with Schema__Browser_Test_Config() as _:
            assert _.headless       is True
            assert _.capture_stderr is True
            assert _.host           == 'localhost'

    def test__init____with_overrides(self):                                     # verify overrides
        with Schema__Browser_Test_Config(headless=False, capture_stderr=False) as _:
            assert _.headless       is False
            assert _.capture_stderr is False
