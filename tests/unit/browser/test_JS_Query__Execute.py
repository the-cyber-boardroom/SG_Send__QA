# ═══════════════════════════════════════════════════════════════════════════════
# Unit tests for JS_Query__Execute
#
# Tests the JS code generation logic — no browser required.
# A lightweight mock records evaluate() calls and returns controlled values.
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                   import TestCase
from osbot_utils.utils.Misc                     import str_to_base64
from sg_send_qa.browser.JS_Query__Execute       import JS_Query__Execute, b64


# ── Minimal mock — records the last JS code evaluated ───────────────────────

class Mock_Page:
    def __init__(self, return_value=None):
        self.last_js   = None
        self.return_value = return_value

    def evaluate(self, js_code):
        self.last_js = js_code
        return self.return_value


# ─────────────────────────────────────────────────────────────────────────────

class test_JS_Query__Execute(TestCase):

    def setUp(self):
        self.mock = Mock_Page()
        self.js   = JS_Query__Execute(raw_page=self.mock)

    # ── b64 helper ────────────────────────────────────────────────────────────

    def test__b64__encodes_string(self):
        assert b64("hello") == str_to_base64("hello")

    def test__b64__converts_non_string(self):
        assert b64(42) == str_to_base64("42")

    # ── evaluate ──────────────────────────────────────────────────────────────

    def test__evaluate__delegates_to_raw_page(self):
        self.mock.return_value = "result"
        assert self.js.evaluate("1 + 1") == "result"
        assert self.mock.last_js == "1 + 1"

    def test__evaluate_iife__wraps_in_iife(self):
        self.js.evaluate_iife("return 42")
        assert self.mock.last_js == "(() => {\nreturn 42\n})()"

    # ── eval_safe ─────────────────────────────────────────────────────────────

    def test__eval_safe__replaces_placeholder_with_atob(self):
        self.js.eval_safe("doSomething({key})", key="my-token")
        expected_b64 = b64("my-token")
        assert f"atob('{expected_b64}')" in self.mock.last_js
        assert "{key}" not in self.mock.last_js

    def test__eval_safe__multiple_placeholders(self):
        self.js.eval_safe("f({a}, {b})", a="x", b="y")
        assert f"atob('{b64('x')}')" in self.mock.last_js
        assert f"atob('{b64('y')}')" in self.mock.last_js

    def test__eval_safe__no_raw_value_in_js(self):                             # XSS: raw value must never appear in JS
        dangerous = "'; DROP TABLE users; --"
        self.js.eval_safe("doSomething({v})", v=dangerous)
        assert dangerous not in self.mock.last_js
        assert "atob(" in self.mock.last_js

    # ── storage ───────────────────────────────────────────────────────────────

    def test__storage_get__encodes_key(self):
        self.js.storage_get("my-key")
        assert f"atob('{b64('my-key')}')" in self.mock.last_js
        assert "localStorage.getItem" in self.mock.last_js

    def test__storage_set__encodes_key_and_value(self):
        self.js.storage_set("token-key", "token-value")
        assert f"atob('{b64('token-key')}')" in self.mock.last_js
        assert f"atob('{b64('token-value')}')" in self.mock.last_js
        assert "localStorage.setItem" in self.mock.last_js

    def test__storage_remove__encodes_key(self):
        self.js.storage_remove("my-key")
        assert f"atob('{b64('my-key')}')" in self.mock.last_js
        assert "localStorage.removeItem" in self.mock.last_js

    def test__storage_clear__clears_all(self):
        self.js.storage_clear()
        assert self.mock.last_js == "localStorage.clear()"

    def test__storage_dump__returns_json_parse(self):
        self.js.storage_dump()
        assert "JSON.parse" in self.mock.last_js

    # ── light DOM reads ───────────────────────────────────────────────────────

    def test__light_text__encodes_selector(self):
        self.js.light_text("#my-el")
        assert f'atob("{b64("#my-el")}")' in self.mock.last_js
        assert "innerText" in self.mock.last_js

    def test__light_value__encodes_selector(self):
        self.js.light_value("#input")
        assert f'atob("{b64("#input")}")' in self.mock.last_js
        assert ".value" in self.mock.last_js

    def test__light_attribute__encodes_selector_and_attr(self):
        self.js.light_attribute("body", "data-ready")
        assert f'atob("{b64("body")}")' in self.mock.last_js
        assert f'atob("{b64("data-ready")}")' in self.mock.last_js
        assert "getAttribute" in self.mock.last_js

    def test__light_property__encodes_selector_and_prop(self):
        self.js.light_property("send-upload", "_state")
        assert f'atob("{b64("send-upload")}")' in self.mock.last_js
        assert f'atob("{b64("_state")}")' in self.mock.last_js

    def test__light_exists__encodes_selector(self):
        self.js.light_exists("#gate")
        assert f'atob("{b64("#gate")}")' in self.mock.last_js
        assert "!== null" in self.mock.last_js

    def test__light_visible__encodes_selector(self):
        self.js.light_visible("#zone")
        assert f'atob("{b64("#zone")}")' in self.mock.last_js
        assert "getBoundingClientRect" in self.mock.last_js

    # ── predicates ────────────────────────────────────────────────────────────

    def test__predicate__light_exists__is_callable_js_function(self):
        pred = self.js.predicate__light_exists("#el")
        assert pred.startswith("() =>")
        assert f'atob("{b64("#el")}")' in pred
        assert "!== null" in pred

    def test__predicate__light_not_exists__is_callable_js_function(self):
        pred = self.js.predicate__light_not_exists("#el")
        assert pred.startswith("() =>")
        assert "=== null" in pred

    def test__predicate__light_property_equals__encodes_all_values(self):
        pred = self.js.predicate__light_property_equals("send-upload", "_state", "complete")
        assert pred.startswith("() =>")
        assert f'atob("{b64("send-upload")}")' in pred
        assert f'atob("{b64("_state")}")' in pred
        assert f'atob("{b64("complete")}")' in pred
        assert "===" in pred

    def test__predicate__light_property_in__encodes_all_values(self):
        pred = self.js.predicate__light_property_in("send-download", "state",
                                                    ["ready", "complete", "error"])
        assert pred.startswith("() =>")
        assert f'atob("{b64("send-download")}")' in pred
        assert f'atob("{b64("state")}")' in pred
        assert f'atob("{b64("ready")}")' in pred
        assert f'atob("{b64("complete")}")' in pred
        assert f'atob("{b64("error")}")' in pred
        assert "indexOf" in pred

    def test__predicate__light_property_equals__no_raw_values_in_js(self):     # XSS: raw values never appear
        pred = self.js.predicate__light_property_equals("send-upload", "_state", "complete")
        assert "send-upload" not in pred
        assert "_state"      not in pred
        assert "complete"    not in pred
