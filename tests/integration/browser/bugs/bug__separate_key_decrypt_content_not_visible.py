"""
Bug: Separate Key decrypt — content not visible in inner_text("body") after decryption.

After entering the correct key on the download page and clicking "Decrypt & View",
the decrypted file content is NOT returned by inner_text("body"). The content appears
to be rendered inside a shadow DOM element OR triggers a file download rather than
an inline display.

This prevents the QA framework from asserting content correctness after separate-key
decryption. The bug affects:
  - tests/integration/browser/test_SG_Send__Browser__Pages__Download.py
  - tests/qa/v030/p0__separate_key/test__separate_key.py (marked xfail strict=True)

Observed in: v0.3.0 UI, local in-memory stack
Reported: 2026-03-25
Status: OPEN — awaiting dev investigation

Brief for dev team:
  The send-download component's behaviour after decrypt is opaque to Playwright.
  Expected: decrypted text/plain content rendered in DOM where inner_text picks it up.
  Actual: inner_text("body") still shows "Decryption key / Decrypt & View" form.
  Next step: inspect send-download.js and send-viewer.js to find where content renders.
"""

from unittest                                           import TestCase
from osbot_utils.testing.Stderr                         import Stderr
from sg_send_qa.browser.SG_Send__Browser__Test_Harness  import SG_Send__Browser__Test_Harness

BUG_CONTENT   = b"Separate-key decrypt content visibility bug — tracking test."
BUG_FILENAME  = "bug-separate-key.txt"


class bug__separate_key_decrypt_content_not_visible(TestCase):                   # Bug tracker: separate key decrypt content invisible
    """These tests PASS (by asserting the known-buggy behaviour).
    When the bug is fixed, these tests will FAIL — flagging that the fix is in
    and the tests should be promoted to proper assertions.
    """

    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().headless(True).setup()
        cls.sg_send = cls.harness.sg_send
        cls.helper  = cls.harness.transfer_helper()
        with cls.harness as _:
            _.set_access_token()

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    def setUp(self):
        Stderr().start()

    def test__bug__separate_key__content_not_in_inner_text_after_decrypt(self):
        """Bug assertion: inner_text("body") does NOT contain the decrypted content.

        When this test FAILS it means the bug was fixed — content is now visible.
        Promote this test to a positive assertion in test_SG_Send__Browser__Pages__Download.py.
        """
        tid, key_b64 = self.helper.upload_encrypted(BUG_CONTENT, BUG_FILENAME,
                                                    content_type="text/plain")

        self.sg_send.page__download_with_id(tid)
        self.sg_send.wait(4000)

        self.sg_send.download__enter_key(key_b64)
        self.sg_send.wait(500)
        self.sg_send.download__click_decrypt()
        self.sg_send.wait(5000)

        text = self.sg_send.visible_text()

        # BUG: content is NOT visible — this assertion passes while bug exists
        assert BUG_CONTENT.decode() not in text, (
            "BUG FIXED: decrypted content is now visible in inner_text! "
            "Promote this to a positive test in test_SG_Send__Browser__Pages__Download.py."
        )
        assert BUG_FILENAME not in text, (
            "BUG FIXED: filename is now visible in inner_text after decrypt! "
            "Promote this to a positive test in test_SG_Send__Browser__Pages__Download.py."
        )

    def test__bug__separate_key__key_form_still_visible_after_decrypt(self):
        """Bug assertion: 'Decryption key' form text is STILL present after decrypt click.

        If this fails, the UI has changed and the form IS dismissed — a positive sign
        that the fix may be underway.
        """
        tid, key_b64 = self.helper.upload_encrypted(BUG_CONTENT, BUG_FILENAME,
                                                    content_type="text/plain")

        self.sg_send.page__download_with_id(tid)
        self.sg_send.wait(4000)

        self.sg_send.download__enter_key(key_b64)
        self.sg_send.wait(500)
        self.sg_send.download__click_decrypt()
        self.sg_send.wait(5000)

        text = self.sg_send.visible_text()

        # BUG: the "Decryption key" form text is still visible after decrypt
        # (i.e. the UI did not transition to a content-visible state)
        assert "Decryption key" in text, (
            "UI behaviour changed: 'Decryption key' form is now gone after decrypt. "
            "Check whether content is now visible — this bug may be partially fixed."
        )
