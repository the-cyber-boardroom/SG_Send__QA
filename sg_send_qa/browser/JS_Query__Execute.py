# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — JS Query Execute (Base Layer)
#
# The single point of contact between Python and the browser's JS runtime.
# Every JS evaluation in the framework goes through this class.
#
# Responsibilities:
#   - Base64 encoding of all Python→JS values (XSS prevention)
#   - Safe evaluation with {placeholder} templates
#   - localStorage helpers
#   - Light DOM reads (text, attribute, value, exists, visible)
#
# This class is the base for JS_Query__Shadow_DOM which adds Shadow DOM
# traversal and predicates on top.
#
# Usage:
#   js = JS_Query__Execute(raw_page=page.page)
#
#   # Safe eval with base64-encoded values
#   js.eval_safe("localStorage.setItem({key}, {value})",
#                key='sgraph-send-token', value='my-token')
#
#   # Light DOM reads
#   js.light_text("title")
#   js.light_attribute("body", "data-ready")
#   js.light_exists("#access-token-input")
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Misc          import str_to_base64


def b64(value):                                                                 # base64 encode for safe JS injection
    return str_to_base64(str(value))


class JS_Query__Execute(Type_Safe):                                             # single point of JS execution — all evals go through here
    raw_page : object = None                                                    # playwright.sync_api.Page

    # ═══════════════════════════════════════════════════════════════════════════
    # Core — evaluate
    # ═══════════════════════════════════════════════════════════════════════════

    def evaluate(self, js_code):                                                # evaluate a JS expression, return result
        return self.raw_page.evaluate(js_code)

    def evaluate_iife(self, js_body):                                           # wrap in IIFE and evaluate
        return self.evaluate(f"(() => {{\n{js_body}\n}})()")

    def eval_safe(self, template, **kwargs):                                    # evaluate with base64-encoded value substitution
        """Replace {name} placeholders with atob('base64value').

        Usage: js.eval_safe("localStorage.setItem({key}, {value})",
                            key='sgraph-send-token', value='my-token')

        Every value is base64-encoded in Python and decoded via atob() in JS.
        The base64 alphabet (A-Za-z0-9+/=) cannot contain quotes, angle
        brackets, or any JS-significant characters — injection is structurally
        impossible.
        """
        for name, value in kwargs.items():
            template = template.replace(f'{{{name}}}', f"atob('{b64(value)}')")
        return self.evaluate(template)

    # ═══════════════════════════════════════════════════════════════════════════
    # localStorage
    # ═══════════════════════════════════════════════════════════════════════════
    # [LIB-2026-04-01-007] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
    def storage_get(self, key):                                                 # read from localStorage
        return self.evaluate(f"localStorage.getItem(atob('{b64(key)}'))")

    def storage_set(self, key, value):                                          # write to localStorage
        self.evaluate(f"localStorage.setItem(atob('{b64(key)}'), atob('{b64(value)}'))")
        return self

    def storage_remove(self, key):                                              # remove from localStorage
        self.evaluate(f"localStorage.removeItem(atob('{b64(key)}'))")
        return self

    def storage_clear(self):                                                    # clear all localStorage
        self.evaluate("localStorage.clear()")
        return self

    def storage_dump(self):                                                     # return all localStorage as dict
        return self.evaluate("JSON.parse(JSON.stringify(localStorage))")

    # ═══════════════════════════════════════════════════════════════════════════
    # Light DOM reads — no shadow traversal
    # ═══════════════════════════════════════════════════════════════════════════
    # [LIB-2026-04-01-008] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
    def light_text(self, selector):                                             # innerText of a light DOM element
        sel_b64 = b64(selector)
        return self.evaluate_iife(
            f'var el = document.querySelector(atob("{sel_b64}"))\n'
            f'return el ? el.innerText.trim() : null')

    def light_text_content(self, selector):                                     # textContent (includes hidden text)
        sel_b64 = b64(selector)
        return self.evaluate_iife(
            f'var el = document.querySelector(atob("{sel_b64}"))\n'
            f'return el ? el.textContent.trim() : null')

    def light_value(self, selector):                                            # .value of an input/textarea
        sel_b64 = b64(selector)
        return self.evaluate_iife(
            f'var el = document.querySelector(atob("{sel_b64}"))\n'
            f'return el ? el.value : null')

    def light_attribute(self, selector, attr_name):                             # getAttribute
        sel_b64  = b64(selector)
        attr_b64 = b64(attr_name)
        return self.evaluate_iife(
            f'var el = document.querySelector(atob("{sel_b64}"))\n'
            f'return el ? el.getAttribute(atob("{attr_b64}")) : null')

    def light_property(self, selector, prop_name):                              # JS property (not attribute) — e.g. _state, checked
        sel_b64  = b64(selector)
        prop_b64 = b64(prop_name)
        return self.evaluate_iife(
            f'var el   = document.querySelector(atob("{sel_b64}"))\n'
            f'var prop = atob("{prop_b64}")\n'
            f'return el ? el[prop] : null')

    def light_exists(self, selector):                                           # is element in the DOM?
        sel_b64 = b64(selector)
        return self.evaluate_iife(
            f'return document.querySelector(atob("{sel_b64}")) !== null')

    def light_visible(self, selector):                                          # is element visible?
        sel_b64 = b64(selector)
        return self.evaluate_iife(
            f'var el = document.querySelector(atob("{sel_b64}"))\n'
            f'if (!el) return false\n'
            f'var rect = el.getBoundingClientRect()\n'
            f'return rect.width > 0 && rect.height > 0') or False

    # ═══════════════════════════════════════════════════════════════════════════
    # Light DOM predicates — JS function strings for wait_for_function
    # ═══════════════════════════════════════════════════════════════════════════
    # [LIB-2026-04-01-009] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
    def predicate__light_exists(self, selector):                                # true when element is present in DOM
        sel_b64 = b64(selector)
        return f'() => document.querySelector(atob("{sel_b64}")) !== null'

    def predicate__light_not_exists(self, selector):                            # true when element has been removed from DOM
        sel_b64 = b64(selector)
        return f'() => document.querySelector(atob("{sel_b64}")) === null'

    def predicate__light_property_equals(self, selector, prop_name, expected):  # true when element[prop] === expected
        sel_b64 = b64(selector)
        prp_b64 = b64(prop_name)
        val_b64 = b64(str(expected))
        return (f'() => {{ '
                f'var el = document.querySelector(atob("{sel_b64}")); '
                f'return el != null && el[atob("{prp_b64}")] === atob("{val_b64}") '
                f'}}')

    def predicate__light_property_in(self, selector, prop_name, values):        # true when element[prop] is in the values list
        sel_b64  = b64(selector)
        prp_b64  = b64(prop_name)
        vals_js  = '[' + ', '.join(f'atob("{b64(v)}")' for v in values) + ']'
        return (f'() => {{ '
                f'var el = document.querySelector(atob("{sel_b64}")); '
                f'if (!el) return false; '
                f'return {vals_js}.indexOf(el[atob("{prp_b64}")]) !== -1 '
                f'}}')
