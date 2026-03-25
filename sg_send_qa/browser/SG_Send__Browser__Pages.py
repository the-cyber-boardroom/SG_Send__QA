# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — Browser Page Primitives (Layer 1)
# Navigation, access gate, upload wizard, download — Shadow DOM aware
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_playwright.playwright.api.Playwright_Page import Playwright_Page
from osbot_utils.decorators.methods.cache_on_self                                import cache_on_self
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.network.safe_uint.Safe_UInt__Port  import Safe_UInt__Port
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url__Server import Safe_Str__Url__Server
from osbot_utils.utils.Http                                                      import url_join_safe
from sg_send_qa.browser.QA_Browser                                               import QA_Browser

DEFAULT__TARGET_SERVER__LOCALHOST = Safe_Str__Url__Server('http://localhost')
DEFAULT__I18N__LANGUAGE_LOCATION = 'en-gb'


class SG_Send__Browser__Pages(Type_Safe):
    headless      : bool                     = True
    target_port   : Safe_UInt__Port          = 0        # todo: see why we are getting an  "ValueError: Safe_UInt__Port does not allow None values" (even when this value is set on the ctor call)
    target_server : Safe_Str__Url__Server    = DEFAULT__TARGET_SERVER__LOCALHOST

    # ═══════════════════════════════════════════════════════════════════════════
    # Raw page access
    # ═══════════════════════════════════════════════════════════════════════════

    @cache_on_self
    def qa_browser(self):
        return QA_Browser(headless=self.headless)

    def chrome(self):                                                           # the Chrome browser wrapper
        return self.qa_browser().chrome()

    def page(self):                                                             # Playwright_Page wrapper
        return self.qa_browser().page()

    def raw_page(self):                                                         # raw playwright.sync_api.Page for locators
        return self.page().page

    # ═══════════════════════════════════════════════════════════════════════════
    # Navigation
    # ═══════════════════════════════════════════════════════════════════════════

    def open(self, path, use_language=True) -> Playwright_Page:                 # navigate to a path under the target server
        url = self.url__for_path(path=path, use_language=use_language)
        self.raw_page().goto(url, wait_until="commit")                         # commit fires on first byte — SG/Send inline scripts may block domcontentloaded
        return self.page()

    def url__target_server(self):                                               # base URL of the local QA server
        return f'{self.target_server}:{self.target_port}/'


    def url__for_locale(self):                                              # join path to base URL
        return url_join_safe(self.url__target_server(), DEFAULT__I18N__LANGUAGE_LOCATION)

    def url__for_path(self, path, use_language=True):                                              # join path to base URL
        if use_language:
            return url_join_safe(self.url__for_locale(), path)
        else:
            return url_join_safe(self.url__target_server(), path)

    def url(self):                                                              # current page URL
        return self.qa_browser().url()

    def title(self):                                                            # current page title
        return self.page().title()

    def screenshot(self, path=''):                                              # capture screenshot
        return self.qa_browser().screenshot(path=path)

    # ═══════════════════════════════════════════════════════════════════════════
    # Page navigation — each route in the v0.3.0 UI
    # ═══════════════════════════════════════════════════════════════════════════

    def page__root(self):                                                       # upload page: /en-gb/
        return self.open("")

    def page__browse(self):                                                     # browse view: /en-gb/browse/
        return self.open("browse")

    def page__download(self):                                                   # download page: /en-gb/download/
        return self.open("download")

    def page__gallery(self):                                                    # gallery view: /en-gb/gallery/
        return self.open("gallery")

    def page__view(self):                                                       # single file viewer: /en-gb/view/
        return self.open("view")

    def page__welcome(self):                                                    # welcome / token activation: /en-gb/welcome/
        return self.open("welcome")

    def page__browse_with_hash(self, transfer_id, key_b64):                     # browse with decrypt hash
        url = f"{self.url__for_locale()}/browse/#{transfer_id}/{key_b64}"      # hash must bypass url_join_safe (it sanitises #)
        return self._open_with_hash(url)

    def page__gallery_with_hash(self, transfer_id, key_b64):                    # gallery with decrypt hash
        url = f"{self.url__for_locale()}/gallery/#{transfer_id}/{key_b64}"
        return self._open_with_hash(url)

    def page__view_with_hash(self, transfer_id, key_b64):                       # view with decrypt hash
        url = f"{self.url__for_locale()}/view/#{transfer_id}/{key_b64}"
        return self._open_with_hash(url)

    def page__download_with_hash(self, transfer_id, key_b64):                   # download with combined link hash
        url = f"{self.url__for_locale()}/download/#{transfer_id}/{key_b64}"
        return self._open_with_hash(url)

    def page__download_with_id(self, transfer_id):                              # download without key (separate key mode)
        url = f"{self.url__for_locale()}/download/#{transfer_id}"
        return self._open_with_hash(url)

    def _open_with_hash(self, url):                                             # navigate using commit — fires on first byte received
        self.raw_page().goto(url, wait_until="commit")                          # SG/Send inline scripts may delay domcontentloaded; commit is safest
        return self

    def page__qa_setup(self):                                                   # minimal page — localStorage only, no JS overhead
        return self.open("_common/qa-setup.html", use_language=False)

    # ═══════════════════════════════════════════════════════════════════════════
    # Storage helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def storage__set_token(self, token):                                        # pre-populate access token via lightweight page
        #self.page__qa_setup()
        #self.js_evaluate(f"QA.setToken('{token}')")                                # security-vuln: vulnerable to XSS on token
        self.js_evaluate(f"localStorage.setItem('sgraph-send-token', '{token}')")   # security-vuln: vulnerable to XSS on token
        return self

    def storage__get_token(self):                                               # read token from localStorage
        self.page__qa_setup()
        return self.js_evaluate("QA.getToken()")

    def storage__clear(self):                                                   # wipe localStorage (clean slate between tests)
        self.page__qa_setup()
        self.js_evaluate("QA.clear()")
        return self

    def storage__dump(self):                                                    # return all localStorage as dict
        self.page__qa_setup()
        return self.js_evaluate("QA.dump()")

    # ═══════════════════════════════════════════════════════════════════════════
    # Wait helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def wait(self, ms=1000):                                                    # explicit wait (ms)
        self.raw_page().wait_for_timeout(ms)
        return self

    def wait_for_page_ready(self, timeout=5000):                                # wait for data-ready attribute on body
        self.raw_page().wait_for_selector("body[data-ready]", timeout=timeout)
        return self

    def wait_for_component(self, tag_name, timeout=5000):                       # wait for a Web Component to emit component-ready
        self.raw_page().wait_for_selector(tag_name, state="attached", timeout=timeout)
        return self

    def wait_for_upload_state(self, state, timeout=10000):                      # wait for upload orchestrator to reach a state
        self.raw_page().wait_for_function(                                      # polls send-upload._state via JS
            f"document.querySelector('send-upload')?._state === '{state}'",
            timeout=timeout,
        )
        return self

    def wait_for_download_state(self, state, timeout=15000):                    # wait for send-download component to reach a state
        self.raw_page().wait_for_function(                                      # states: loading|entry|ready|decrypting|complete|error
            f"document.querySelector('send-download')?.state === '{state}'",
            timeout=timeout,
        )
        return self

    def wait_for_download_states(self, states, timeout=15000):                  # wait for any of multiple send-download states
        states_js = str(states).replace("'", '"')                               # JS-safe list
        self.raw_page().wait_for_function(
            f"(function(){{ var s = document.querySelector('send-download')?.state; "
            f"return {states_js}.indexOf(s) !== -1; }})()",
            timeout=timeout,
        )
        return self

    def wait_for_selector_hidden(self, selector, timeout=5000):                 # wait for an element to disappear
        self.raw_page().wait_for_selector(selector, state="hidden", timeout=timeout)
        return self

    def wait_for_selector_visible(self, selector, timeout=5000):                # wait for an element to appear
        self.raw_page().wait_for_selector(selector, state="visible", timeout=timeout)
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # State queries
    # ═══════════════════════════════════════════════════════════════════════════

    def invoke__javascript(self, expression):           # todo: add this method to the Playwright_Page class
        return self.js_evaluate(expression)

    def js_evaluate(self, expression):                                                   # run JS in page context
        return self.raw_page().evaluate(expression)

    def visible_text(self):                                                     # visible text only (no <script> content)
        return self.raw_page().inner_text("body")

    def upload_state(self):                                                     # current upload wizard state
        return self.js_evaluate("document.querySelector('send-upload')?._state")

    def is_access_gate_visible(self):                                           # is the token entry form showing?
        return self.raw_page().locator("#access-token-input").is_visible(timeout=2000)

    def is_upload_zone_visible(self):                                           # is the upload drop zone visible? (inside shadow DOM)
        return self.raw_page().locator("upload-step-select").is_visible(timeout=2000)

    # ═══════════════════════════════════════════════════════════════════════════
    # Access gate — light DOM (send-access-gate uses innerHTML, not shadow)
    # ═══════════════════════════════════════════════════════════════════════════

    def access_gate__enter_token(self, token):                                  # type token into the gate input
        gate_input = self.raw_page().locator("#access-token-input")
        gate_input.wait_for(state="visible", timeout=5000)
        gate_input.fill(token)
        return self

    def access_gate__submit(self):                                              # click the Go button; wait for gate to respond
        self.raw_page().locator("#access-token-submit").click()
        # wait for gate to dismiss (upload zone appears) or reject (gate stays visible with error)
        try:
            self.raw_page().wait_for_function(                                  # either gate gone OR upload zone appeared
                "document.querySelector('#access-token-input') === null "
                "|| document.querySelector('upload-step-select') !== null",
                timeout=3000,
            )
        except Exception:
            pass                                                                # gate stayed — handled by caller
        return self

    def access_gate__enter_and_submit(self, token):                             # combined: fill + submit
        self.access_gate__enter_token(token)
        self.access_gate__submit()
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Upload wizard — Shadow DOM aware
    #
    # Component tree:
    #   <send-upload>                    (light DOM orchestrator)
    #     <upload-step-select>           (shadow DOM — #file-input, #drop-zone)
    #     <upload-step-delivery>         (shadow DOM)
    #     <upload-step-share>            (shadow DOM — .share-card[data-mode])
    #     <upload-step-confirm>          (shadow DOM)
    #     <upload-step-progress>         (shadow DOM)
    #     <upload-step-done>             (shadow DOM — #combined-link, #simple-token)
    #   #upload-next-btn                 (light DOM — rendered by orchestrator)
    # ═══════════════════════════════════════════════════════════════════════════

    def upload__set_file(self, filename, content_bytes, mime_type="text/plain"):     # set file via input (pierces shadow DOM)
        file_input = self.raw_page().locator("upload-step-select #file-input")
        file_input.wait_for(state="attached", timeout=5000)
        file_input.set_input_files({"name"    : filename     ,
                                    "mimeType": mime_type    ,
                                    "buffer"  : content_bytes})
        self.wait(800)                                                              # let wizard auto-advance to delivery
        return self

    def upload__click_next(self):                                                   # click the Next / Encrypt & Upload button
        btn = self.raw_page().locator("#upload-next-btn")
        btn.wait_for(state="visible", timeout=5000)
        btn.click()
        self.wait(500)
        return self

    def upload__select_share_mode(self, mode):                                      # click a share mode card: 'combined', 'token', 'separate'
        card = self.raw_page().locator(f'upload-step-share [data-mode="{mode}"]')
        card.wait_for(state="visible", timeout=5000)
        card.click()
        self.wait(500)                                                              # let wizard auto-advance to confirm
        return self

    def upload__wait_for_complete(self, timeout=20000):                             # wait for upload to finish
        self.wait_for_upload_state("complete", timeout=timeout)
        return self

    def upload__get_combined_link(self):                                            # extract combined link from done step
        el = self.raw_page().locator("upload-step-done #combined-link")
        #el.wait_for(state="visible", timeout=5000)
        return el.text_content().strip()

    def upload__get_friendly_token(self):                                           # extract friendly token from done step
        #document.querySelector("upload-step-done").shadowRoot.querySelector("#simple-token").innerText
        #el = self.raw_page().locator("upload-step-done #simple-token")
        # todo: explore how to make code like the one below to be more generic since it doesn't have the timeout problem that locator has
        outer_selector =  "upload-step-done"
        inner_selector = "#simple-token"
        js__get_simple_token = f"""
var outer_selector =  "{outer_selector}"
var inner_selector = "{inner_selector}"
var node = document.querySelector(outer_selector).shadowRoot.querySelector(inner_selector)
if (node) {{
    result = node.innerText
}} else {{
    result = null
}}
result
"""
        result = self.invoke__javascript(js__get_simple_token)
        return result

        #el.wait_for(state="visible", timeout=5000)
        return el.text_content().strip()

    def upload__get_full_link(self):                                                # extract full link (token mode) from done step
        el = self.raw_page().locator("upload-step-done #full-link")
        el.wait_for(state="visible", timeout=5000)
        return el.text_content().strip()

    def upload__get_link_only(self):                                                # extract link-only URL (separate key mode)
        el = self.raw_page().locator("upload-step-done #link-only")
        el.wait_for(state="visible", timeout=5000)
        return el.text_content().strip()

    def upload__get_decryption_key(self):                                           # extract decryption key (separate key mode)
        el = self.raw_page().locator("upload-step-done #decryption-key")
        el.wait_for(state="visible", timeout=5000)
        return el.text_content().strip()

    # ═══════════════════════════════════════════════════════════════════════════
    # Download page — light DOM (send-download uses this.innerHTML)
    # ═══════════════════════════════════════════════════════════════════════════

    def download__enter_key(self, key):                                             # enter decryption key on download page
        key_input = self.raw_page().locator("#key-input")
        key_input.wait_for(state="visible", timeout=5000)
        key_input.fill(key)
        return self

    def download__click_decrypt(self, timeout=20000):                               # click Decrypt & wait for state change
        btn = self.raw_page().locator("#decrypt-btn")
        btn.wait_for(state="visible", timeout=5000)
        btn.click()
        self.wait_for_download_states(["complete", "error"], timeout=timeout)       # wait for decrypt pipeline to finish
        return self

    def download__enter_manual_id(self, text):                                      # enter transfer ID in manual entry form
        entry = self.raw_page().locator("#entry-input")
        entry.wait_for(state="visible", timeout=5000)
        entry.fill(text)
        return self

    def download__submit_manual_entry(self, timeout=10000):                         # submit manual entry; wait for response
        self.raw_page().locator("#entry-btn").click()
        # after submit: may reach ready/complete/error OR stay in entry with inline error
        self.wait_for_download_states(["ready", "complete", "error", "entry"], timeout=timeout)
        return self

    def download__wait_for_content(self, text, timeout=15000):                      # wait for decrypted text to appear
        self.raw_page().locator(f"text={text}").wait_for(state="visible", timeout=timeout)
        return self

    def download__save_button_visible(self):                                        # is the Save Locally button present?
        return self.raw_page().locator("#sf-save").is_visible(timeout=3000)

    # ═══════════════════════════════════════════════════════════════════════════
    # Workflows — multi-step sequences (Layer 2 preview)
    # ═══════════════════════════════════════════════════════════════════════════

    def workflow__upload_combined(self, token, filename, content_bytes,              # full combined link upload flow
                                  mime_type="text/plain"                ):
        self.page__root()
        self.wait_for_page_ready()
        if self.is_access_gate_visible():
            self.access_gate__enter_and_submit(token)
        self.upload__set_file(filename, content_bytes, mime_type)
        self.upload__click_next()                                                   # delivery → share
        self.upload__select_share_mode("combined")                                  # auto-advances to confirm
        self.upload__click_next()                                                   # confirm → encrypt & upload
        self.upload__wait_for_complete()
        return self.upload__get_combined_link()

    def workflow__upload_friendly_token(self, token, filename, content_bytes,        # full simple token upload flow
                                        mime_type="text/plain"               ):
        self.page__root()
        self.wait_for_page_ready()
        if self.is_access_gate_visible():
            self.access_gate__enter_and_submit(token)
        self.upload__set_file(filename, content_bytes, mime_type)
        self.upload__click_next()                                                   # delivery → share
        self.upload__select_share_mode("token")                                     # auto-advances to confirm
        self.upload__click_next()                                                   # confirm → encrypt & upload
        self.upload__wait_for_complete()
        return self.upload__get_friendly_token()

    def workflow__upload_separate_key(self, token, filename, content_bytes,          # full separate key upload flow
                                      mime_type="text/plain"              ):
        self.page__root()
        self.wait_for_page_ready()
        if self.is_access_gate_visible():
            self.access_gate__enter_and_submit(token)
        self.upload__set_file(filename, content_bytes, mime_type)
        self.upload__click_next()                                                   # delivery → share
        self.upload__select_share_mode("separate")                                  # auto-advances to confirm
        self.upload__click_next()                                                   # confirm → encrypt & upload
        self.upload__wait_for_complete()
        link = self.upload__get_link_only()
        key  = self.upload__get_decryption_key()
        return link, key