"""BUG P0: send-download.js deep-link fix strips the encryption key.

Introduced by commit: "fix send-download.js (v0.3.0): strip deep-link path
from hash before token parse"

Root cause:
  The PLR-006 "fix" strips everything after the FIRST '/' from the hash.
  But the normal browse URL format is #transferId/encryptionKey — the FIRST
  '/' separates the transferId from the key. Stripping at the first '/'
  discards the encryption key entirely.

  Broken code in send-download.js _parseUrl():
    const hash = _fullHash.includes('/')
                   ? _fullHash.slice(0, _fullHash.indexOf('/'))  // strips key!
                   : _fullHash;
    // ...
    const i = hash.indexOf('/');   // -1, because key was stripped
    if (i > 0) { ... }             // never reached
    else { this.transferId = hash; // hashKey never set → decryption fails }

  Result: sd.hashKey = undefined → decryption fails → state='ready', zipTree=[]
  → browse tree never renders. ALL non-friendly-token browse transfers are broken.

Impact:
  - P0: every browse/download page load with a #tid/key URL silently fails
  - The zip is downloaded but cannot be decrypted (no key)
  - Users see a perpetual loading/ready state with no content
  - Only friendly-token URLs (word-word-NNNN) are unaffected (no '/' in token)

Correct fix in send-download.js _parseUrl():
  For regular tokens: strip path suffix after the SECOND slash (keeping key).
  For friendly tokens: strip path suffix after the FIRST slash (token has no key).

    const firstSlash = _fullHash.indexOf('/');
    const firstPart  = firstSlash > 0 ? _fullHash.slice(0, firstSlash) : _fullHash;
    let hash;
    if (firstSlash < 0) {
        hash = _fullHash;  // no slash — no path suffix
    } else if (typeof FriendlyCrypto !== 'undefined' && FriendlyCrypto.isFriendlyToken(firstPart)) {
        hash = firstPart;  // friendly token: strip path after first slash
    } else {
        const secondSlash = _fullHash.indexOf('/', firstSlash + 1);
        hash = secondSlash > 0 ? _fullHash.slice(0, secondSlash) : _fullHash;
    }

This test PASSES while the bug exists (hashKey absent / zipTree empty).
When fixed (hashKey present, browse tree renders), this test FAILS — delete it.

RELEASE BLOCKER: Do NOT deploy v0.3.1 until this is fixed.
"""

import io
import zipfile

import pytest

pytestmark = [pytest.mark.v031]


class TestBugSendDownloadDeepLinkStripsKey:

    @pytest.fixture(autouse=True)
    def _setup(self, transfer_helper, ui_url):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("test.md", "# Test\n\nContent.")
        buf.seek(0)
        tid, key = transfer_helper.upload_encrypted(buf.read(), "key-strip-bug.zip")
        self._url = f"{ui_url}/en-gb/browse/#{tid}/{key}"

    def test_p0_bug_encryption_key_stripped_from_hash(self, page, screenshots):
        """P0 BUG: sd.hashKey is absent because the deep-link fix strips the key.

        PASSES while the bug exists (hashKey absent, zipTree empty).
        FAILS when fixed (hashKey set, browse tree renders) → delete this file.
        """
        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(3_000)
        screenshots.capture(page, "p0_bug_deeplink_01_blank", "Browse loaded — should be blank (bug)")

        result = page.evaluate("""() => {
            const sd = document.querySelector('send-download');
            return {
                hashKey:   sd ? sd.hashKey   : 'NO_ELEMENT',
                zipTree:   sd && sd.zipTree ? sd.zipTree.length : 0,
                state:     sd ? sd.state     : 'NO_ELEMENT',
            };
        }""")

        screenshots.capture(page, "p0_bug_deeplink_02_state", f"State: {result}")

        # PASSES while bug exists: hashKey is absent (undefined/null) → decryption fails
        assert not result.get("hashKey"), (
            "P0 BUG FIXED: sd.hashKey is now set. "
            "The deep-link fix no longer strips the encryption key. "
            "Delete this bug test file and re-enable/add the PLR test suite."
        )

    def test_p0_bug_browse_tree_never_renders(self, page, screenshots):
        """P0 BUG: Browse tree is empty because decryption fails without the key.

        PASSES while the bug exists (empty tree).
        FAILS when fixed (tree has files) → delete this file.
        """
        page.goto(self._url)
        page.wait_for_selector("body[data-ready]", timeout=10_000)
        page.wait_for_timeout(3_000)
        screenshots.capture(page, "p0_bug_deeplink_03_tree", "Browse tree — should be empty (bug)")

        tree_items = page.locator(".sb-tree__file-name").all_text_contents()

        # PASSES while bug exists: tree is empty
        assert not tree_items, (
            "P0 BUG FIXED: Browse tree now renders files. "
            "The encryption key is no longer stripped. "
            "Delete this bug test file."
        )
