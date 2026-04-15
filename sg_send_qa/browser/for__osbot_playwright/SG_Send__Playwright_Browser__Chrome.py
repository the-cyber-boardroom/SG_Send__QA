# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send — Playwright Chrome launcher
# Skips OSBot-Playwright's install path, uses playwright-installed binary
# Adds --no-sandbox for Linux (GH Actions, Docker, CI)
# ═══════════════════════════════════════════════════════════════════════════════

import platform

from osbot_utils.helpers.duration.decorators.print_duration import print_duration

from osbot_playwright.playwright.api.Playwright_Browser         import Playwright_Browser
from osbot_playwright.playwright.api.Playwright_CLI             import Playwright_CLI
from osbot_playwright.playwright.api.Playwright_Process         import Playwright_Process
from osbot_utils.utils.Misc                                     import random_port
from osbot_playwright.playwright.api.Playwright_Browser__Chrome import Playwright_Browser__Chrome
from sg_send_qa.local_servers.QA__Local_Browser import QA__Local_Browser
from sg_send_qa.browser import shared_playwright_state          # shared instance set by conftest.py fixture




class SG_Send__Playwright_Process(Playwright_Process):                          # adds --no-sandbox on Linux (required for GH Actions / Docker)

    def start_process(self):
        if platform.system() == 'Linux':                                        # Chrome on Linux CI needs --no-sandbox
            import subprocess
            from osbot_utils.utils.Files import path_combine, folder_create

            if self.process_running():
                self.logger.error("There is already a chromium process running")
                return False
            if self.debug_port is None:
                raise Exception("[Playwright_Process] in start_process the debug_port value was not set")
            if self.browser_path is None:
                raise Exception("[Playwright_Process] in start_process the browser_path value was not set")

            browser_data_folder = self.path_data_folder()
            params = [self.browser_path                                         ,
                      f'--remote-debugging-port={self.debug_port}'              ,
                      f'--user-data-dir={browser_data_folder}'                  ,
                      '--use-mock-keychain'                                     ,
                      '--no-sandbox'                                            ]

            if self.headless:
                params.append('--headless')

            folder_create(browser_data_folder)
            process = subprocess.Popen(params)
            self.save_process_details(process, self.debug_port)

            if self.wait_for_debug_port() is False:
                raise Exception(f"in browser_start_process, port {self.debug_port} was not open after process start")

            self.logger.info(f"started process id {process.pid} with debug port {self.debug_port}")
            return True
        else:
            return super().start_process()                                      # macOS/Windows — use parent (no sandbox issue)


class _Shared_Playwright_Context_Manager:                                       # thin wrapper that reuses an already-running Playwright instance
    """Returned by playwright_context_manager() when a shared instance exists.

    Mimics the sync_playwright() context-manager protocol so that
    Playwright_Browser.playwright() (which calls .start()) works correctly
    without starting a second asyncio event loop.
    """
    def __init__(self, p):
        self._p = p

    def start(self):
        return self._p                                                          # return the existing instance; do NOT call .start() on it

    def __enter__(self):
        return self._p

    def __exit__(self, *_):
        pass                                                                    # never stop the shared instance


class SG_Send__Playwright_Browser__Chrome(Playwright_Browser__Chrome):

    #qa_local_browser : QA__Local_Browser                                      # todo: refactor this to be part of the OSBot_Playwright codebase (and be a Type_Safe class)

    def __init__(self, port=None, headless=True):
        Playwright_Browser.__init__(self)                                       # skip Playwright_Browser__Chrome.__init__, call grandparent
        self._browser           = None
        self.debug_port         = port or random_port()
        self.headless           = headless
        self.browser_name       = 'chromium'
        #self.browser_exec_path  = chromium_executable_path()
        self.browser_exec_path  = QA__Local_Browser().chromium_executable_path()
        self.playwright_process = SG_Send__Playwright_Process(                  # use our process class (adds --no-sandbox on Linux)
                                      browser_path = self.browser_exec_path ,
                                      debug_port   = self.debug_port        ,
                                      headless     = self.headless          )
        self.playwright_cli     = Playwright_CLI()

    def playwright_context_manager(self):                                       # reuse shared instance from conftest.py if available
        if shared_playwright_state.instance is not None:
            return _Shared_Playwright_Context_Manager(shared_playwright_state.instance)
        from playwright.sync_api import sync_playwright
        return sync_playwright()

    def stop_playwright_and_process(self):                                      # don't stop shared playwright instance
        if shared_playwright_state.instance is not None:                        # shared instance is owned by conftest.py — only stop the Chrome process
            self.playwright_process.stop_process()
            return self.playwright_process.process_running() is False
        return super().stop_playwright_and_process()                            # owned by us — stop both playwright and process