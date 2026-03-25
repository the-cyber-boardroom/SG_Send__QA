# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — JS Query for Shadow DOM
#
# Inherits JS_Query__Execute (base64 encoding, safe eval, localStorage, light DOM).
# Adds Shadow DOM traversal at arbitrary depth and JS predicates for wait_for_function.
#
# Usage:
#   query = JS_Query__Shadow_DOM(raw_page=page.page)
#
#   # Single shadow level
#   query.text("upload-step-done", "#simple-token")
#
#   # Multi-level shadow
#   query.text("send-upload", "upload-step-done", "#simple-token")
#
#   # Wait then read (caller composes)
#   page.wait_for_function(query.predicate__text("upload-step-done", "#simple-token"))
#   text = query.text("upload-step-done", "#simple-token")
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.utils.Misc                         import str_to_base64
from sg_send_qa.browser.JS_Query__Execute           import JS_Query__Execute


class JS_Query__Shadow_DOM(JS_Query__Execute):                                  # shadow DOM traversal + predicates

    # ═══════════════════════════════════════════════════════════════════════════
    # Core JS builder — traverses shadow boundaries at arbitrary depth
    # ═══════════════════════════════════════════════════════════════════════════

    def _js_resolve(self, *selectors):                                          # build JS that navigates host → shadowRoot → ... → leaf
        """Build JS code that resolves an element through N levels of Shadow DOM.

        Args: variable selectors from outermost host to innermost target.
              e.g. ("send-upload", "upload-step-done", "#simple-token")

        All selectors are base64-encoded for XSS safety.
        Returns: (js_code, final_var_name)
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
                lines.append(f'if (!{prev}.shadowRoot) return null')
                lines.append(f'var {var} = {prev}.shadowRoot.querySelector(atob("{b64}"))')
                lines.append(f'if (!{var}) return null')

        return '\n'.join(lines), f"n{len(selectors)-1}"

    # ═══════════════════════════════════════════════════════════════════════════
    # Pure reads — instant, return None if element missing
    # ═══════════════════════════════════════════════════════════════════════════

    def text(self, *selectors):                                                 # innerText of the deepest element
        resolve, var = self._js_resolve(*selectors)
        return self.evaluate_iife(f'{resolve}\nreturn {var}.innerText.trim()')

    def html(self, *selectors):                                                 # innerHTML of the deepest element
        resolve, var = self._js_resolve(*selectors)
        return self.evaluate_iife(f'{resolve}\nreturn {var}.innerHTML')

    def attribute(self, *selectors, attr_name):                                 # attribute value
        attr_b64 = str_to_base64(attr_name)
        resolve, var = self._js_resolve(*selectors)
        return self.evaluate_iife(f'{resolve}\nreturn {var}.getAttribute(atob("{attr_b64}"))')

    def value(self, *selectors):                                                # .value (for inputs)
        resolve, var = self._js_resolve(*selectors)
        return self.evaluate_iife(f'{resolve}\nreturn {var}.value')

    def exists(self, *selectors):                                               # does the element exist in the DOM?
        resolve, var = self._js_resolve(*selectors)
        return self.evaluate_iife(f'{resolve}\nreturn true') or False

    def visible(self, *selectors):                                              # is the element visible?
        resolve, var = self._js_resolve(*selectors)
        return self.evaluate_iife(
            f'{resolve}\n'
            f'var rect = {var}.getBoundingClientRect()\n'
            f'return rect.width > 0 && rect.height > 0') or False

    def count(self, host_selector, inner_selector):                             # count matching elements inside shadow root
        host_b64  = str_to_base64(host_selector)
        inner_b64 = str_to_base64(inner_selector)
        return self.evaluate_iife(
            f'var host = document.querySelector(atob("{host_b64}"))\n'
            f'if (!host || !host.shadowRoot) return 0\n'
            f'return host.shadowRoot.querySelectorAll(atob("{inner_b64}")).length') or 0

    def texts(self, host_selector, inner_selector):                             # list of innerText for all matches
        host_b64  = str_to_base64(host_selector)
        inner_b64 = str_to_base64(inner_selector)
        return self.evaluate_iife(
            f'var host = document.querySelector(atob("{host_b64}"))\n'
            f'if (!host || !host.shadowRoot) return []\n'
            f'return Array.from(host.shadowRoot.querySelectorAll(atob("{inner_b64}")))'
            f'.map(n => n.innerText.trim())') or []

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
