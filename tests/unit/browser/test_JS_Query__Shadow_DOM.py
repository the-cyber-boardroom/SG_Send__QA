# ═══════════════════════════════════════════════════════════════════════════════
# Unit tests for JS_Query__Shadow_DOM
#
# Tests the shadow DOM JS code generation — no browser required.
# Verifies: _js_resolve selectors are base64-encoded, methods build correct JS,
# predicates return callable function strings.
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                       import TestCase
from osbot_utils.utils.Misc                         import str_to_base64
from sg_send_qa.browser.JS_Query__Execute           import b64
from sg_send_qa.browser.JS_Query__Shadow_DOM        import JS_Query__Shadow_DOM


class Mock_Page:
    def __init__(self, return_value=None):
        self.last_js      = None
        self.return_value = return_value

    def evaluate(self, js_code):
        self.last_js = js_code
        return self.return_value


class test_JS_Query__Shadow_DOM(TestCase):

    def setUp(self):
        self.mock  = Mock_Page()
        self.query = JS_Query__Shadow_DOM(raw_page=self.mock)

    # ── Inherits JS_Query__Execute ────────────────────────────────────────────

    def test__inherits_execute__storage_set(self):                              # JS_Query__Shadow_DOM inherits all Execute methods
        self.query.storage_set("k", "v")
        assert "localStorage.setItem" in self.mock.last_js

    def test__inherits_execute__light_text(self):
        self.query.light_text("#el")
        assert "innerText" in self.mock.last_js

    # ── _js_resolve ───────────────────────────────────────────────────────────

    def test___js_resolve__requires_at_least_two_selectors(self):
        with self.assertRaises(ValueError):
            self.query._js_resolve("only-one")

    def test___js_resolve__two_selectors__encodes_both(self):
        js, var = self.query._js_resolve("upload-step-done", "#simple-token")
        assert f'atob("{b64("upload-step-done")}")' in js
        assert f'atob("{b64("#simple-token")}")' in js
        assert var == "n1"

    def test___js_resolve__three_selectors__builds_chain(self):
        js, var = self.query._js_resolve("send-upload", "upload-step-done", "#simple-token")
        assert f'atob("{b64("send-upload")}")' in js
        assert f'atob("{b64("upload-step-done")}")' in js
        assert f'atob("{b64("#simple-token")}")' in js
        assert "shadowRoot" in js
        assert var == "n2"

    def test___js_resolve__no_raw_selector_strings_in_js(self):                # XSS: raw selectors never appear
        js, _ = self.query._js_resolve("send-upload", "#token")
        assert "send-upload" not in js
        assert "#token"      not in js

    def test___js_resolve__null_guards_on_each_step(self):                     # each level returns null if missing
        js, _ = self.query._js_resolve("host-el", "#inner")
        assert "return null" in js

    # ── text / html / value / exists / visible ────────────────────────────────

    def test__text__builds_innerText_read(self):
        self.query.text("upload-step-done", "#simple-token")
        assert "innerText" in self.mock.last_js
        assert f'atob("{b64("upload-step-done")}")' in self.mock.last_js

    def test__html__builds_innerHTML_read(self):
        self.query.html("host-el", "#inner")
        assert "innerHTML" in self.mock.last_js

    def test__value__builds_value_read(self):
        self.query.value("host-el", "#input")
        assert ".value" in self.mock.last_js

    def test__exists__returns_false_when_page_returns_none(self):
        self.mock.return_value = None
        result = self.query.exists("host-el", "#missing")
        assert result is False

    def test__exists__returns_true_when_page_returns_truthy(self):
        self.mock.return_value = True
        result = self.query.exists("host-el", "#present")
        assert result is True

    def test__visible__returns_false_when_page_returns_none(self):
        self.mock.return_value = None
        result = self.query.visible("host-el", "#hidden")
        assert result is False

    def test__count__builds_querySelectorAll(self):
        self.query.count("host-el", ".items")
        assert "querySelectorAll" in self.mock.last_js
        assert f'atob("{b64("host-el")}")' in self.mock.last_js
        assert f'atob("{b64(".items")}")' in self.mock.last_js

    def test__texts__builds_map_innerText(self):
        self.query.texts("host-el", ".item")
        assert "map" in self.mock.last_js
        assert "innerText" in self.mock.last_js

    # ── predicates ────────────────────────────────────────────────────────────

    def test__predicate__exists__is_callable_js_function(self):
        pred = self.query.predicate__exists("host-el", "#inner")
        assert pred.startswith("() =>")
        assert "return true" in pred
        assert "return false" in pred                                           # guard replaces "return null"

    def test__predicate__exists__no_return_null(self):                          # "return null" must be replaced with "return false"
        pred = self.query.predicate__exists("host-el", "#inner")
        assert "return null" not in pred

    def test__predicate__text__checks_innerText(self):
        pred = self.query.predicate__text("host-el", "#el")
        assert "innerText" in pred
        assert "!!" in pred                                                     # truthy check

    def test__predicate__text_equals__encodes_expected(self):
        pred = self.query.predicate__text_equals("host-el", "#el", expected="hello")
        assert f'atob("{b64("hello")}")' in pred
        assert "===" in pred
        assert "hello" not in pred.replace(b64("hello"), "")                   # raw value not present

    def test__predicate__visible__checks_bounding_rect(self):
        pred = self.query.predicate__visible("host-el", "#el")
        assert "getBoundingClientRect" in pred
        assert "width" in pred
        assert "height" in pred

    def test__predicate__all_start_with_arrow_function(self):                  # all predicates are callable JS arrow functions
        preds = [
            self.query.predicate__exists("h", "#i"),
            self.query.predicate__text("h", "#i"),
            self.query.predicate__text_equals("h", "#i", expected="x"),
            self.query.predicate__visible("h", "#i"),
        ]
        for pred in preds:
            assert pred.strip().startswith("() =>"), f"not an arrow function: {pred[:60]}"

    def test__predicate__all_encode_selectors(self):                           # no raw selector strings in any predicate
        host_b64 = b64("send-upload")
        inner_b64 = b64("#simple-token")
        preds = [
            self.query.predicate__exists("send-upload", "#simple-token"),
            self.query.predicate__text("send-upload", "#simple-token"),
            self.query.predicate__visible("send-upload", "#simple-token"),
        ]
        for pred in preds:
            assert host_b64  in pred,  f"host b64 missing: {pred[:80]}"
            assert inner_b64 in pred,  f"inner b64 missing: {pred[:80]}"
            assert "send-upload"    not in pred
            assert "#simple-token" not in pred
