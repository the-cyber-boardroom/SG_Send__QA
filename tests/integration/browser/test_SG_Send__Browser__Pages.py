# ═══════════════════════════════════════════════════════════════════════════════
# Tests for SG_Send__Browser__Pages — Browser page primitives and workflows
# Requires: local QA stack running on localhost:10062
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                          import TestCase
from sg_send_qa.browser.SG_Send__Browser__Test_Harness import SG_Send__Browser__Test_Harness


class test_SG_Send__Browser__Pages(TestCase):                                   # Navigation — pages load with correct titles

    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().setup()
        cls.sg_send = cls.harness.sg_send()

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    # ── Page navigation ──────────────────────────────────────────────────────

    def test_page__root(self):                                                  # upload page loads
        self.sg_send.page__root()
        assert self.sg_send.title() == 'SG/Send — Zero-knowledge encrypted file sharing'

    def test_page__browse(self):                                                # browse page loads
        self.sg_send.page__browse()
        assert self.sg_send.title() == 'SG/Send — Browse Files'

    def test_page__download(self):                                              # download page loads
        self.sg_send.page__download()
        assert self.sg_send.title() == 'SG/Send — Download & Decrypt'

    def test_page__gallery(self):                                               # gallery page loads
        self.sg_send.page__gallery()
        assert self.sg_send.title() == 'SG/Send — Gallery'

    def test_page__view(self):                                                  # view page loads
        self.sg_send.page__view()
        assert self.sg_send.title() == 'SG/Send — View File'

    def test_page__welcome(self):                                               # welcome page loads
        self.sg_send.page__welcome()
        assert self.sg_send.title() == 'SG/Send — Welcome'


