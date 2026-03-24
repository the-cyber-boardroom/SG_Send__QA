from unittest                                   import TestCase
from sg_send_qa.browser.SG_Send__Browser__Pages import SG_Send__Browser__Pages

class test_SG_Send__Browser__Pages(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sg_send__pages = SG_Send__Browser__Pages()
        cls.sg_send__pages.qa_browser.headless = False

    def test_page__browse(self):
        page = self.sg_send__pages.page__browse()
        assert page.title() == 'SG/Send — Browse Files'

    def test_page__download(self):
        page = self.sg_send__pages.page__download()
        assert page.title() == 'SG/Send — Download & Decrypt'

    def test_page__galley(self):
        page = self.sg_send__pages.page__gallery()
        assert page.title() == 'SG/Send — Gallery'

    def test_page__root(self):
        page = self.sg_send__pages.page__root()
        assert page.title() == 'SG/Send — Zero-knowledge encrypted file sharing'


