from unittest                       import TestCase
from sg_send_qa.browser.QA_Browser  import QA_Browser


class test_QA_Browser__with_browser(TestCase):                                  # Integration — launches real browser
    qa_browser : QA_Browser

    @classmethod
    def setUpClass(cls):
        cls.qa_browser = QA_Browser(headless=True)
        cls.qa_browser.chrome().browser_process__start_if_needed()

    @classmethod
    def tearDownClass(cls):
        cls.qa_browser.stop()

    def test_chrome(self):                                                      # browser process starts and is healthy
        chrome = self.qa_browser.chrome()
        assert chrome is not None
        assert self.qa_browser.healthy() is True

    def test_page(self):                                                        # page is created on first access
        page = self.qa_browser.page()
        assert page            is not None
        assert page.is_closed() is False

    def test_open(self):                                                        # navigate to a URL
        page = self.qa_browser.open('https://www.google.com')
        assert 'google.com' in self.qa_browser.url()
        html = self.qa_browser.html()
        assert '<html' in html.lower()
        title = self.qa_browser.js('document.title')
        assert type(title) is str
        assert len(title)  > 0
        page.close()

