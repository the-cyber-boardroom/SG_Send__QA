from osbot_playwright.playwright.api.Playwright_Browser         import Playwright_Browser
from osbot_playwright.playwright.api.Playwright_CLI             import Playwright_CLI
from osbot_playwright.playwright.api.Playwright_Process         import Playwright_Process
from osbot_utils.utils.Misc                                     import random_port
from osbot_playwright.playwright.api.Playwright_Browser__Chrome import Playwright_Browser__Chrome, CHROME_BROWSER_NAME


def chromium_executable_path():                                                 # resolve Chromium binary from playwright's own registry
    from playwright.sync_api import sync_playwright                             # late import — avoids circular deps
    pw   = sync_playwright().start()
    path = pw.chromium.executable_path
    pw.stop()
    return path


# todo: convert this to Type_Save class
class SG_Send__Playwright_Browser__Chrome(Playwright_Browser__Chrome):


    def __init__(self, port=None, headless=True):
        Playwright_Browser.__init__(self)                                       # skip Playwright_Browser__Chrome.__init__, call grandparent
        self._browser           = None
        self.debug_port         = port or random_port()
        self.headless           = headless
        self.browser_name       = 'chromium'
        self.browser_exec_path  = chromium_executable_path()
        self.playwright_process = Playwright_Process(browser_path = self.browser_exec_path ,
                                                     debug_port   = self.debug_port        ,
                                                     headless     = self.headless           )
        self.playwright_cli     = Playwright_CLI()