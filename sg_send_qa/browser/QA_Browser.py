# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — Persistent Browser via OSBot-Playwright
# Wraps Playwright_Browser__Chrome for reusable, debug-friendly browser sessions
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.base_classes.Kwargs_To_Self                            import Kwargs_To_Self as Type_Safe
from osbot_playwright.playwright.api.Playwright_Browser__Chrome         import Playwright_Browser__Chrome
from osbot_playwright.playwright.api.Playwright_Page                    import Playwright_Page
from sg_send_qa.browser.for__osbot_playwright.SG_Send__Playwright_Browser__Chrome import SG_Send__Playwright_Browser__Chrome

DEFAULT_BROWSER_PORT = 10070                                                    # fixed port — browser survives across runs
DEFAULT_HEADLESS     = False                                                    # default to visible for debugging
DEFAULT_VIEWPORT     = dict(width=1280, height=800)                             # matches QA screenshot viewport



class QA_Browser(Type_Safe):                                                    # Persistent browser for QA testing and debugging
    port     : int  = DEFAULT_BROWSER_PORT                                      # CDP debug port — fixed so process is reusable
    headless : bool = DEFAULT_HEADLESS                                          # False = visible browser window

    _chrome  : Playwright_Browser__Chrome = None                                # lazy-initialised browser wrapper
    _page    : Playwright_Page            = None                                # current active page

    def chrome(self) -> Playwright_Browser__Chrome:                             # lazy-init the browser process
        if self._chrome is None:
            self._chrome = SG_Send__Playwright_Browser__Chrome(port     = self.port    ,
                                                               headless = self.headless)
        return self._chrome

    def page(self) -> Playwright_Page:                                          # get or create the active page
        return self.chrome().page()
        if self._page is None or self._page.is_closed():
            self._page = self.chrome().new_page()
        return self._page

    def open(self, url: str) -> Playwright_Page:                                # navigate and return the page
        page = self.page()
        page.open(url)
        return page

    def url(self) -> str:                                                       # current page URL
        return self.page().url()

    def screenshot(self, path: str = '') -> str:                                # capture screenshot, return file path
        return self.page().screenshot(path=path) if path else self.page().screenshot()

    def html(self) -> str:                                                      # raw HTML of current page
        return self.page().html_raw()

    def js(self, expression: str):                                              # run JS in page context
        return self.page().page.evaluate(expression)

    def healthy(self) -> bool:                                                  # is the browser process alive?
        try:
            return self.chrome().playwright_process.healthy()
        except Exception:
            return False

    def stop(self) -> bool:                                                     # stop browser and cleanup
        if self._chrome:
            result       = self._chrome.stop_playwright_and_process()
            #self._chrome = None                                                # can't do this on type safe objects
            #self._page   = None
            return result
        return False