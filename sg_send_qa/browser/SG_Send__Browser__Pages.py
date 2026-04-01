# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — Browser Page Primitives (Layer 1)
# Navigation, access gate, upload wizard, download — Shadow DOM aware
#
# All Python→JS communication goes through self.js() (JS_Query__Shadow_DOM).
# No raw js_evaluate() with string interpolation. No locator() for DOM reads.
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_playwright.playwright.api.Playwright_Page                             import Playwright_Page
from osbot_utils.decorators.methods.cache_on_self                                import cache_on_self
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.network.safe_uint.Safe_UInt__Port  import Safe_UInt__Port
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url__Server import Safe_Str__Url__Server
from osbot_utils.utils.Http                                                      import url_join_safe
from osbot_utils.utils.Misc                                                      import str_to_base64
from sg_send_qa.browser.JS_Query__Shadow_DOM                                     import JS_Query__Shadow_DOM
from sg_send_qa.browser.QA_Browser                                               import QA_Browser
from sg_send_qa.browser.Schema__Browse_Page                                      import Schema__Browse_Page
from sg_send_qa.browser.Schema__Download_Page                                    import Schema__Download_Page
from sg_send_qa.browser.Schema__Gallery_Page                                     import Schema__Gallery_Page
from sg_send_qa.browser.Schema__Upload_Page                                      import Schema__Upload_Page
from sg_send_qa.browser.Schema__Viewer_Page                                      import Schema__Viewer_Page

DEFAULT__TARGET_SERVER__LOCALHOST = Safe_Str__Url__Server('http://localhost')
DEFAULT__I18N__LANGUAGE_LOCATION = 'en-gb'

# this class needs to be split into smaller classes (specially the code specific to a particular page or flow)
class SG_Send__Browser__Pages(Type_Safe):
    headless      : bool                     = True
    target_port   : Safe_UInt__Port          = 0        # [LIB-2026-04-01-010] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
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

    def raw_page(self):                                                         # raw playwright.sync_api.Page for locators/waits
        return self.page().page

    def js(self):                                                               # JS query layer — ALL JS goes through here
        return JS_Query__Shadow_DOM(raw_page=self.raw_page())

    # ═══════════════════════════════════════════════════════════════════════════
    # Navigation
    # ═══════════════════════════════════════════════════════════════════════════

    def open(self, path, use_language=True, wait_for_ready=True) -> Playwright_Page:  # navigate; wait for app init by default
        url = self.url__for_path(path=path, use_language=use_language)
        self.raw_page().goto(url, wait_until="commit")                         # commit fires on first byte; domcontentloaded blocked by SG/Send inline scripts
        if wait_for_ready:
            self.wait_for_page_ready()                                         # event: body[data-ready] set by app init
        return self.page()

    def url__target_server(self):                                               # base URL of the local QA server
        return f'{self.target_server}:{self.target_port}/'

    def url__for_locale(self):                                                  # locale-prefixed base: http://host:port/en-gb
        return url_join_safe(self.url__target_server(), DEFAULT__I18N__LANGUAGE_LOCATION)

    def url__for_path(self, path, use_language=True):                           # full URL for a route path
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

    def _open_with_hash(self, url, wait_for_ready=True):                        # navigate to a URL with hash fragment; wait for app init
        self.raw_page().goto(url, wait_until="commit")                          # hash routes use same SG/Send app shell
        if wait_for_ready:
            self.wait_for_page_ready()
        return self

    def page__qa_setup(self):                                                   # minimal static page — localStorage only, no JS app init
        return self.open("_common/qa-setup.html", use_language=False,
                         wait_for_ready=False)                                  # qa-setup.html is static HTML; no app init, no body[data-ready]

    # ═══════════════════════════════════════════════════════════════════════════
    # Storage helpers — all localStorage ops go through js().storage_*
    # ═══════════════════════════════════════════════════════════════════════════

    def storage__set_token(self, token):                                        # pre-populate access token in localStorage
        self.js().storage_set('sgraph-send-token', token)                      # base64-safe — no XSS risk
        return self

    def storage__get_token(self):                                               # read access token from localStorage
        return self.js().storage_get('sgraph-send-token')

    def storage__set(self, key, value):                                         # write an arbitrary localStorage entry
        self.js().storage_set(key, value)
        return self

    def storage__get(self, key):                                                # read an arbitrary localStorage entry
        return self.js().storage_get(key)

    def storage__clear(self):                                                   # wipe all localStorage
        self.js().storage_clear()
        return self

    def storage__dump(self):                                                    # return all localStorage as dict
        return self.js().storage_dump()

    # ═══════════════════════════════════════════════════════════════════════════
    # Wait helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def wait_for_page_ready(self, timeout=5000):                                # wait for app init: body[data-ready] set by SG/Send bootstrap
        self.raw_page().wait_for_selector("body[data-ready]", timeout=timeout)
        return self

    def wait_for_component(self, tag_name, timeout=5000):                       # wait for a Web Component to be attached to DOM
        self.raw_page().wait_for_selector(tag_name, state="attached", timeout=timeout)
        return self

    def wait_for_upload_state(self, state, timeout=10000):                      # wait for upload wizard to reach a state
        pred = self.js().predicate__light_property_equals("send-upload", "_state", state)
        self.raw_page().wait_for_function(pred, timeout=timeout)
        return self

    def wait_for_upload_states(self, states, timeout=10000):                    # wait for upload wizard to reach any of the given states
        pred = self.js().predicate__light_property_in("send-upload", "_state", states)
        self.raw_page().wait_for_function(pred, timeout=timeout)
        return self

    def wait_for_download_state(self, state, timeout=15000):                    # wait for send-download to reach a state
        pred = self.js().predicate__light_property_equals("send-download", "state", state)
        self.raw_page().wait_for_function(pred, timeout=timeout)                # states: loading|entry|ready|decrypting|complete|error
        return self

    def wait_for_download_states(self, states, timeout=15000):                  # wait for send-download to reach any of the given states
        pred = self.js().predicate__light_property_in("send-download", "state", states)
        self.raw_page().wait_for_function(pred, timeout=timeout)
        return self

    def wait_for_selector_hidden(self, selector, timeout=5000):                 # wait for an element to disappear (Playwright selector wait)
        self.raw_page().wait_for_selector(selector, state="hidden", timeout=timeout)
        return self

    def wait_for_selector_visible(self, selector, timeout=5000):                # wait for an element to appear (Playwright selector wait)
        self.raw_page().wait_for_selector(selector, state="visible", timeout=timeout)
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # State queries
    # ═══════════════════════════════════════════════════════════════════════════

    def visible_text(self):                                                     # visible text of the page body
        return self.js().light_text("body")

    def upload_state(self):                                                     # current upload wizard state (_state property)
        return self.js().light_property("send-upload", "_state")

    def download_state(self):                                                   # current download component state
        return self.js().light_property("send-download", "state")

    def is_access_gate_visible(self):                                           # is the token entry form showing?
        return self.js().light_visible("#access-token-input")

    def is_upload_zone_visible(self):                                           # is the upload drop zone present?
        return self.js().light_visible("upload-step-select")

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
        gate_b64   = str_to_base64("#access-token-input")
        upload_b64 = str_to_base64("upload-step-select")
        pred = (f'() => {{'                                                     # gate dismissed (input gone) OR upload zone appeared
                f' return document.querySelector(atob("{gate_b64}")) === null'
                f' || document.querySelector(atob("{upload_b64}")) !== null'
                f'}}')
        try:
            self.raw_page().wait_for_function(pred, timeout=3000)
        except Exception:
            pass                                                                # gate stayed (wrong token) — caller checks state
        return self

    def access_gate__enter_and_submit(self, token):                             # combined: fill + submit
        self.access_gate__enter_token(token)
        self.access_gate__submit()
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Upload wizard — Shadow DOM aware
    #
    # Component tree:
    #   <send-upload>                    (light DOM orchestrator, ._state)
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
        self.wait_for_upload_states(['file-ready', 'choosing-delivery'])            # wait for wizard to advance from idle after file selection
        return self

    def upload__click_next(self):                                                   # click the Next / Encrypt & Upload button
        btn = self.raw_page().locator("#upload-next-btn")
        btn.wait_for(state="visible", timeout=5000)
        state_before = self.upload_state()                                          # capture state before click
        btn.click()
        # wait for state to change from whatever it was before — works regardless of which step we're on
        pre_b64 = str_to_base64(str(state_before))
        pred    = (f'() => {{'
                   f' var el = document.querySelector(atob("{str_to_base64("send-upload")}")); '
                   f' return el != null && el[atob("{str_to_base64("_state")}")] !== atob("{pre_b64}") '
                   f'}}')
        try:
            self.raw_page().wait_for_function(pred, timeout=3000)
        except Exception:
            pass                                                                    # upload may jump quickly through states; caller handles completion
        return self

    def upload__select_share_mode(self, mode):                                      # click a share mode card: 'combined', 'token', 'separate'
        card = self.raw_page().locator(f'upload-step-share [data-mode="{mode}"]')
        card.wait_for(state="visible", timeout=5000)
        card.click()
        self.wait_for_upload_state('confirming')                                    # wait for wizard to advance from choosing-share → confirming
        return self

    def upload__wait_for_complete(self, timeout=20000):                             # wait for upload to finish
        self.wait_for_upload_state("complete", timeout=timeout)
        return self

    def upload__get_combined_link(self):                                            # extract combined link from done step (shadow DOM)
        return self.js().text("upload-step-done", "#combined-link")

    def upload__get_friendly_token(self):                                           # extract friendly token from done step (shadow DOM)
        return self.js().text("upload-step-done", "#simple-token")

    def upload__get_full_link(self):                                                # extract full link (token mode) from done step (shadow DOM)
        return self.js().text("upload-step-done", "#full-link")

    def upload__get_link_only(self):                                                # extract link-only URL (separate key mode) from done step (shadow DOM)
        return self.js().text("upload-step-done", "#link-only")

    def upload__get_decryption_key(self):                                           # extract decryption key (separate key mode) from done step (shadow DOM)
        return self.js().text("upload-step-done", "#decryption-key")

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

    def download__wait_for_content(self, text, timeout=15000):                      # wait for decrypted text to appear in light DOM
        self.raw_page().locator(f"text={text}").wait_for(state="visible", timeout=timeout)
        return self

    def download__save_button_visible(self):                                        # is the Save Locally button present?
        return self.js().light_visible("#sf-save")

    # ═══════════════════════════════════════════════════════════════════════════
    # Workflows — multi-step sequences (Layer 2 preview)
    # ═══════════════════════════════════════════════════════════════════════════

    def workflow__upload_combined(self, token, filename, content_bytes,              # full combined link upload flow
                                  mime_type="text/plain"                ):
        self.page__root()
        if self.is_access_gate_visible():
            self.access_gate__enter_and_submit(token)
        self.upload__set_file(filename, content_bytes, mime_type)
        self.upload__click_next()                                                    # delivery → share
        self.upload__select_share_mode("combined")                                   # auto-advances to confirm
        self.upload__click_next()                                                    # confirm → encrypt & upload
        self.upload__wait_for_complete()
        return self.upload__get_combined_link()

    def workflow__upload_friendly_token(self, token, filename, content_bytes,        # full simple token upload flow
                                        mime_type="text/plain"               ):
        self.page__root()
        if self.is_access_gate_visible():
            self.access_gate__enter_and_submit(token)
        self.upload__set_file(filename, content_bytes, mime_type)
        self.upload__click_next()                                                    # delivery → share
        self.upload__select_share_mode("token")                                      # auto-advances to confirm
        self.upload__click_next()                                                    # confirm → encrypt & upload
        self.upload__wait_for_complete()
        return self.upload__get_friendly_token()

    def workflow__upload_separate_key(self, token, filename, content_bytes,          # full separate key upload flow
                                      mime_type="text/plain"              ):
        self.page__root()
        if self.is_access_gate_visible():
            self.access_gate__enter_and_submit(token)
        self.upload__set_file(filename, content_bytes, mime_type)
        self.upload__click_next()                                                    # delivery → share
        self.upload__select_share_mode("separate")                                   # auto-advances to confirm
        self.upload__click_next()                                                    # confirm → encrypt & upload
        self.upload__wait_for_complete()
        link = self.upload__get_link_only()
        key  = self.upload__get_decryption_key()
        return link, key

    # ═══════════════════════════════════════════════════════════════════════════
    # Page model extraction — snapshot current page state into a Type_Safe schema
    # ═══════════════════════════════════════════════════════════════════════════

    def _transfer_id_from_url(self) -> str:                                         # parse transfer ID from hash: /browse/#tid/key → tid
        fragment = self.url().split('#')[-1] if '#' in self.url() else ''
        return fragment.split('/')[0] if fragment else ''

    def extract__upload_page(self) -> Schema__Upload_Page:                          # snapshot upload wizard state
        return Schema__Upload_Page(
            state           = self.upload_state()                                     or '',
            file_name       = self.js().text("upload-step-select", "#file-name")      or '',
            share_link      = self.js().text("upload-step-done",   "#combined-link")  or '',
            friendly_token  = self.js().text("upload-step-done",   "#simple-token")   or '',
            is_gate_visible = self.is_access_gate_visible()                               ,
        )

    # [LIB-2026-04-01-011] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
    def extract__download_page(self) -> Schema__Download_Page:                      # snapshot download/decrypt state
        return Schema__Download_Page(
            state                = self.download_state()                          or '',
            is_key_input_visible = self.js().light_visible("#key-input")              ,
            content_text         = self.visible_text()                            or '',
            error_message        = self.js().light_text(".error-message")         or '',
            transfer_id          = self._transfer_id_from_url()                   or '',
        )

    def extract__browse_page(self) -> Schema__Browse_Page:                          # snapshot browse view state
        return Schema__Browse_Page(
            state         = self.download_state()                                 or '',
            content_text  = self.visible_text()                                   or '',
            error_message = self.js().light_text(".error-message")                or '',
            transfer_id   = self._transfer_id_from_url()                          or '',
        )

    def extract__gallery_page(self) -> Schema__Gallery_Page:                        # snapshot gallery view state
        file_count_text = self.js().light_text(".gallery-count")                    # selector TBC — confirm against live DOM
        try:
            file_count = int(file_count_text) if file_count_text else 0
        except (ValueError, TypeError):
            file_count = 0
        return Schema__Gallery_Page(
            state         = self.download_state()                                 or '',
            file_count    = file_count                                                ,
            content_text  = self.visible_text()                                   or '',
            error_message = self.js().light_text(".error-message")                or '',
            transfer_id   = self._transfer_id_from_url()                          or '',
        )

    def extract__viewer_page(self) -> Schema__Viewer_Page:                          # snapshot single-file viewer state
        return Schema__Viewer_Page(
            state         = self.download_state()                                 or '',
            file_name     = self.js().light_text(".viewer-filename")              or '',  # selector TBC — confirm against live DOM
            content_text  = self.visible_text()                                   or '',
            error_message = self.js().light_text(".error-message")                or '',
            transfer_id   = self._transfer_id_from_url()                          or '',
        )
