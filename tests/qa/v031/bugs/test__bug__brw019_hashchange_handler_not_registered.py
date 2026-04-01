"""BUG: BRW-019 hashchange handler is never registered.

Root cause:
  send-browse-v031.js patches SendDownload.prototype.connectedCallback to
  register a hashchange listener. But the <send-download> element (browse/index.html
  line 36) is parsed and upgraded BEFORE the script tags (lines 49+) run.

  Execution order on the browse page:
    1. HTML parsed up to line 36 → <send-download> element in DOM (unupgraded)
    2. send-download.js runs → customElements.define() called → element upgraded
       → connectedCallback fires (UNPATCHED version)
    3. send-browse-v031.js runs → patches SendDownload.prototype.connectedCallback
       (too late — connectedCallback already fired for the live element)

  Result: sd._v031HashHandler is never set; window.addEventListener('hashchange',
  ...) is never called. Changing the hash (e.g. via the friendly-token entry form)
  has no effect.

Fix needed in send-browse-v031.js (BRW-019 IIFE):
  After patching the prototype, also apply to any already-connected instances:

    document.querySelectorAll('send-download').forEach(function(el) {
        if (!el._v031HashHandler) {
            el._v031HashHandler = function() { ... };
            window.addEventListener('hashchange', el._v031HashHandler);
        }
    });

This test PASSES while the bug exists (handler absent).
When the fix ships, _v031HashHandler IS set → this test FAILS →
delete this file and promote test_brw019_hashchange_loads_new_transfer from p4.
"""

import pytest

pytestmark = [pytest.mark.v031]


class TestBugBrw019:
    @pytest.fixture(autouse=True)
    def _setup(self, transfer_helper, ui_url):
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("file.md", "# Test")
        buf.seek(0)
        tid, key = transfer_helper.upload_encrypted(buf.read(), "brw019-bug.zip")
        self._url = f"{ui_url}/en-gb/browse/#{tid}/{key}"

    def test_brw019_bug_handler_not_registered(self, page, screenshots):
        """BRW-019 BUG: _v031HashHandler is absent because connectedCallback
        fires before send-browse-v031.js patches the prototype.

        PASSES while the bug exists.
        FAILS when fixed → delete this file, promote the BRW-019 test in p4/.
        """
        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(1_500)
        screenshots.capture(page, "brw019_bug_01_loaded", "Browse loaded — checking hashchange handler")

        has_handler = page.evaluate("""() => {
            const sd = document.querySelector('send-download');
            return !!(sd && sd._v031HashHandler);
        }""")

        # PASSES while bug exists (handler absent).
        # When fixed (handler present), this assertion fails — that is the signal.
        assert not has_handler, (
            "BRW-019 bug FIXED: _v031HashHandler is now registered on the "
            "send-download element. Delete this bug test file and promote "
            "test_brw019_hashchange_loads_new_transfer from p4/ to the main suite."
        )
