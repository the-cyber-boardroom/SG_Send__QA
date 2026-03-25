# ═══════════════════════════════════════════════════════════════════════════════
# Tests for JS_Query__Shadow_DOM
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase
from osbot_utils.utils.Misc                                                     import str_to_base64
from sg_send_qa.browser.JS_Query__Shadow_DOM                                    import JS_Query__Shadow_DOM
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                          import SG_Send__Browser__Test_Harness


# ═══════════════════════════════════════════════════════════════════════════════
# Unit tests — JS generation, no browser
# ═══════════════════════════════════════════════════════════════════════════════

class test_JS_Query__Shadow_DOM(TestCase):

    def test__js_resolve__two_levels(self):                                     # host + inner
        query = JS_Query__Shadow_DOM()
        js, var = query._js_resolve("upload-step-done", "#simple-token")
        assert 'atob('                  in js                                   # base64 encoded
        assert 'document.querySelector' in js                                   # starts from document
        assert '.shadowRoot.'           in js                                   # pierces shadow
        assert var                      == 'n1'                                 # final variable

    def test__js_resolve__three_levels(self):                                   # host → inner host → leaf
        query = JS_Query__Shadow_DOM()
        js, var = query._js_resolve("send-upload", "upload-step-done", "#token")
        assert js.count('shadowRoot')   == 2                                    # two shadow boundaries
        assert var                      == 'n2'

    def test__js_resolve__rejects_single_selector(self):                        # must have at least host + inner
        query = JS_Query__Shadow_DOM()
        with self.assertRaises(ValueError):
            query._js_resolve("#only-one")

    def test__js_resolve__base64_encoding(self):                                # selectors are base64 encoded
        query = JS_Query__Shadow_DOM()
        js, _ = query._js_resolve("my-component", "#my-element")
        assert str_to_base64("my-component") in js
        assert str_to_base64("#my-element")  in js
        assert "my-component"            not in js                              # raw selector NOT in JS
        assert "#my-element"             not in js

    def test__predicate__exists(self):                                          # returns JS function string
        query = JS_Query__Shadow_DOM()
        pred = query.predicate__exists("upload-step-done", "#simple-token")
        assert pred.startswith('() => {')
        assert 'return true'  in pred
        assert 'return false' in pred                                           # null replaced with false

    def test__predicate__text_equals(self):                                     # expected value is also base64 encoded
        query = JS_Query__Shadow_DOM()
        pred = query.predicate__text_equals("host", "#el", expected="hello")
        assert str_to_base64("hello") in pred
        assert "hello"            not in pred                                   # raw value NOT in JS


# ═══════════════════════════════════════════════════════════════════════════════
# Integration tests — against live SG/Send Shadow DOM
# ═══════════════════════════════════════════════════════════════════════════════

class test_JS_Query__Shadow_DOM__live(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().headless(True).setup()
        cls.sg_send = cls.harness.sg_send
        cls.query   = JS_Query__Shadow_DOM(raw_page=cls.sg_send.raw_page())
        with cls.harness as _:
            _.set_access_token()
        cls.sg_send.page__root()

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    # ── Light DOM ────────────────────────────────────────────────────────────

    def test_light_text__page_title(self):
        text = self.query.light_text("title")
        assert 'SG/Send' in text

    def test_light_attribute__body_data_ready(self):
        val = self.query.light_attribute("body", "data-ready")
        assert val == 'true'

    # ── Shadow DOM — existence ───────────────────────────────────────────────

    def test_exists__upload_step_select(self):                                  # upload step exists in shadow DOM
        assert self.query.exists("send-upload", "upload-step-select") is True

    def test_exists__nonexistent(self):                                         # missing element returns False
        assert self.query.exists("send-upload", "#does-not-exist") is False

    def test_exists__nonexistent_host(self):                                    # missing host returns False
        assert self.query.exists("no-such-component", "#anything") is False

    # ── Shadow DOM — visibility ──────────────────────────────────────────────

    def test_visible__upload_step_select(self):                                 # visible component
        assert self.query.visible("send-upload", "upload-step-select") is True

    # ── Predicates ───────────────────────────────────────────────────────────

    def test_predicate__exists__evaluates_true(self):                           # predicate works with evaluate
        pred = self.query.predicate__exists("send-upload", "upload-step-select")
        result = self.sg_send.raw_page().evaluate(pred)
        assert result is True

    def test_predicate__exists__evaluates_false(self):
        pred = self.query.predicate__exists("send-upload", "#nope")
        result = self.sg_send.raw_page().evaluate(pred)
        assert result is False
