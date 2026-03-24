# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Harness_State__Persistence
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from sg_send_qa.browser.Harness_State__Persistence                              import Harness_State__Persistence, Schema__Harness_State


class test_Schema__Harness_State(TestCase):                                     # Unit tests — pure data class

    def test__init____defaults(self):
        with Schema__Harness_State() as _:
            assert _.api_port        == 0
            assert _.ui_port         == 0
            assert _.ui_build_folder == ''
            assert _.ui_version      == ''
            assert _.access_token    == ''
            assert _.chrome_port     == 0

    def test__init____with_values(self):
        with Schema__Harness_State(api_port=54321, ui_port=63960, access_token='test-token') as _:
            assert _.api_port     == 54321
            assert _.ui_port      == 63960
            assert _.access_token == 'test-token'


