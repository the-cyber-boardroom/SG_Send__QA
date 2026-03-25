# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — JS Query Helper for Shadow DOM
#
# Playwright's locator API pierces Shadow DOM for interactions (click, fill)
# but doesn't reliably extract text or attributes from shadow roots.
#
# This helper provides:
#   - Pure reads (text, attribute, visibility, count) — instant, return None if missing
#   - JS predicates — expression strings for wait_for_function (no timeout baked in)
#   - Multi-level shadow traversal — arbitrary depth (host → shadow → host → shadow)
#   - XSS-safe — all selectors base64-encoded via str_to_base64/atob
#
# Usage:
#   query = JS_Query__Shadow_DOM(raw_page=page.page)
#
#   # Pure read
#   text = query.text("upload-step-done", "#simple-token")
#
#   # Multi-level shadow
#   text = query.text("send-upload", "upload-step-done", "#simple-token")
#
#   # Wait then read (caller composes)
#   page.wait_for_function(query.predicate__text("upload-step-done", "#simple-token"))
#   text = query.text("upload-step-done", "#simple-token")
#
#   # Check before acting
#   if query.exists("upload-step-done", "#simple-token"):
#       text = query.text("upload-step-done", "#simple-token")
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe import Type_Safe
from osbot_utils.utils.Misc          import str_to_base64


class JS_Query__Shadow_DOM(Type_Safe):
    raw_page : object = None                                                    # playwright sync_api.Page (untyped to avoid import dep)

    # ═══════════════════════════════════════════════════════════════════════════
    # Core JS builder — traverses shadow boundaries at arbitrary depth
    # ═══════════════════════════════════════════════════════════════════════════

    def _js_resolve(self, *selectors):                                          # build JS that navigates host → shadowRoot → host → shadowRoot → leaf
        """Build JS code that resolves an element through N levels of Shadow DOM.

        Args: variable selectors from outermost host to innermost target.
              e.g. ("send-upload", "upload-step-done", "#simple-token")

        First selector: document.querySelector(sel)
        Middle selectors: .shadowRoot.querySelector(sel)
        Last selector: .shadowRoot.querySelector(sel)

        All selectors are base64-encoded for XSS safety.
        """
        if len(selectors) < 2:
            raise ValueError("Need at least 2 selectors: host + inner element")

        lines = []
        for i, selector in enumerate(selectors):
            b64 = str_to_base64(selector)
            var = f"n{i}"
            if i == 0:
                lines.append(f'var {var} = document.querySelector(atob("{b64}"))')
                lines.append(f'if (!{var}) return null')
            else:
                prev = f"n{i-1}"
                if i < len(selectors):                                          # need to go through shadowRoot for all except first
                    lines.append(f'if (!{prev}.shadowRoot) return null')
                    lines.append(f'var {var} = {prev}.shadowRoot.querySelector(atob("{b64}"))')
                    lines.append(f'if (!{var}) return null')

        return '\n'.join(lines), f"n{len(selectors)-1}"                         # return (js_code, final_var_name)

    def _evaluate(self, js_body):                                               # wrap in IIFE and evaluate
        js = f"() => {{\n{js_body}\n}}"
        return self.raw_page.evaluate(js)

    # ═══════════════════════════════════════════════════════════════════════════
    # Pure reads — instant, return None if element missing
    # ═══════════════════════════════════════════════════════════════════════════

    def text(self, *selectors):                                                 # innerText of the deepest element
        resolve, var = self._js_resolve(*selectors)
        return self._evaluate(f'{resolve}\nreturn {var}.innerText.trim()')

    def html(self, *selectors):                                                 # innerHTML of the deepest element
        resolve, var = self._js_resolve(*selectors)
        return self._evaluate(f'{resolve}\nreturn {var}.innerHTML')

    def attribute(self, *selectors, attr_name):                                 # attribute value
        attr_b64 = str_to_base64(attr_name)
        resolve, var = self._js_resolve(*selectors)
        return self._evaluate(f'{resolve}\nreturn {var}.getAttribute(atob("{attr_b64}"))')

    def value(self, *selectors):                                                # .value (for inputs)
        resolve, var = self._js_resolve(*selectors)
        return self._evaluate(f'{resolve}\nreturn {var}.value')

    def exists(self, *selectors):                                               # does the element exist in the DOM?
        resolve, var = self._js_resolve(*selectors)
        return self._evaluate(f'{resolve}\nreturn true') or False

    def visible(self, *selectors):                                              # is the element visible? (not just in DOM)
        resolve, var = self._js_resolve(*selectors)
        return self._evaluate(f'{resolve}\n'
                              f'var rect = {var}.getBoundingClientRect()\n'
                              f'return rect.width > 0 && rect.height > 0') or False

    def count(self, host_selector, inner_selector):                             # count matching elements inside shadow root
        host_b64  = str_to_base64(host_selector)
        inner_b64 = str_to_base64(inner_selector)
        return self._evaluate(
            f'var host = document.querySelector(atob("{host_b64}"))\n'
            f'if (!host || !host.shadowRoot) return 0\n'
            f'return host.shadowRoot.querySelectorAll(atob("{inner_b64}")).length'
        ) or 0

    def texts(self, host_selector, inner_selector):                             # list of innerText for all matches
        host_b64  = str_to_base64(host_selector)
        inner_b64 = str_to_base64(inner_selector)
        return self._evaluate(
            f'var host = document.querySelector(atob("{host_b64}"))\n'
            f'if (!host || !host.shadowRoot) return []\n'
            f'return Array.from(host.shadowRoot.querySelectorAll(atob("{inner_b64}")))'
            f'.map(n => n.innerText.trim())'
        ) or []

    # ═══════════════════════════════════════════════════════════════════════════
    # JS predicates — expression strings for wait_for_function
    # These return JS code (not results). The caller passes them to:
    #   raw_page.wait_for_function(predicate, timeout=N)
    # ═══════════════════════════════════════════════════════════════════════════

    def predicate__exists(self, *selectors):                                    # true when element exists in DOM
        resolve, var = self._js_resolve(*selectors)
        lines = resolve.replace('return null', 'return false')
        return f'() => {{ {lines}; return true }}'

    def predicate__text(self, *selectors):                                      # true when element has non-empty text
        resolve, var = self._js_resolve(*selectors)
        lines = resolve.replace('return null', 'return false')
        return f'() => {{ {lines}; return !!{var}.innerText.trim() }}'

    def predicate__text_equals(self, *selectors, expected):                     # true when text matches expected
        expected_b64 = str_to_base64(expected)
        resolve, var = self._js_resolve(*selectors)
        lines = resolve.replace('return null', 'return false')
        return f'() => {{ {lines}; return {var}.innerText.trim() === atob("{expected_b64}") }}'

    def predicate__visible(self, *selectors):                                   # true when element is visible
        resolve, var = self._js_resolve(*selectors)
        lines = resolve.replace('return null', 'return false')
        return (f'() => {{ {lines}; '
                f'var r = {var}.getBoundingClientRect(); '
                f'return r.width > 0 && r.height > 0 }}')

    # ═══════════════════════════════════════════════════════════════════════════
    # Light DOM convenience — no shadow traversal needed
    # ═══════════════════════════════════════════════════════════════════════════

    def light_text(self, selector):                                             # innerText from light DOM
        b64 = str_to_base64(selector)
        return self._evaluate(
            f'var el = document.querySelector(atob("{b64}"))\n'
            f'return el ? el.innerText.trim() : null')

    def light_attribute(self, selector, attr_name):                             # attribute from light DOM
        sel_b64  = str_to_base64(selector)
        attr_b64 = str_to_base64(attr_name)
        return self._evaluate(
            f'var el = document.querySelector(atob("{sel_b64}"))\n'
            f'return el ? el.getAttribute(atob("{attr_b64}")) : null')

    def light_value(self, selector):                                            # .value from light DOM input
        b64 = str_to_base64(selector)
        return self._evaluate(
            f'var el = document.querySelector(atob("{b64}"))\n'
            f'return el ? el.value : null')
