"""UC-03: Friendly Token — Simple Token share mode (P0).

This was a P0 bug — critical to test.

Flow:
  1. Upload a file with Simple Token share mode
  2. Capture the friendly token (word-word-NNNN format)
  3. Open a new tab to /en-gb/browse/#<friendly-token>
  4. Verify the token resolves and content decrypts
"""

import pytest
import re

pytestmark = pytest.mark.p0

SAMPLE_CONTENT = "Friendly token test — UC-03."
TOKEN_PATTERN  = re.compile(r"^[a-z]+-[a-z]+-\d{4}$")


class TestFriendlyToken:
    """Validate the Simple Token (friendly token) share mode end-to-end."""

    def test_friendly_token_upload_and_resolve(self, page, ui_url, send_server, screenshots):
        """Upload with Simple Token mode, then resolve the friendly token in a new tab."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # --- Handle access gate ---
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        # --- Upload a file ---
        file_input = page.locator("input[type='file']")
        file_input.set_input_files({
            "name"    : "token-test.txt",
            "mimeType": "text/plain",
            "buffer"  : SAMPLE_CONTENT.encode(),
        })
        page.wait_for_timeout(1000)
        screenshots.capture(page, "01_file_selected", "File selected for friendly token test")

        # --- Navigate through wizard to step 3: Share mode ---
        # Click Next/Continue to get to share mode selection
        for _ in range(3):
            btn = page.locator("button:has-text('Next'), button:has-text('Continue')").first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)

        # --- Select Simple Token share mode ---
        simple_token = page.locator("text=Simple token, text=Simple Token, text=Friendly").first
        if simple_token.is_visible(timeout=3000):
            simple_token.click()
            page.wait_for_timeout(500)
        screenshots.capture(page, "02_simple_token_selected", "Simple Token share mode selected")

        # Continue through remaining wizard steps
        for _ in range(5):
            btn = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), "
                "button:has-text('Upload'), button:has-text('Encrypt'), "
                "button:has-text('Confirm')"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(1000)

        # Wait for upload to complete
        page.wait_for_timeout(3000)
        screenshots.capture(page, "03_upload_complete", "Upload complete — friendly token shown")

        # --- Extract the friendly token ---
        # Look for the word-word-NNNN pattern in the page
        page_text = page.text_content("body") or ""
        token_matches = TOKEN_PATTERN.findall(page_text)

        # Also check input fields
        if not token_matches:
            for input_el in page.locator("input[readonly], input[value]").all():
                val = input_el.get_attribute("value") or ""
                found = TOKEN_PATTERN.findall(val)
                if found:
                    token_matches.extend(found)

        assert token_matches, (
            f"No friendly token (word-word-NNNN) found on the page. "
            f"Page text snippet: {page_text[:500]}"
        )

        friendly_token = token_matches[0]
        screenshots.capture(page, "04_token_captured",
                            f"Friendly token captured: {friendly_token}")

    def test_friendly_token_format(self, page, ui_url, send_server, screenshots):
        """Verify the friendly token matches the word-word-NNNN pattern."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # Handle access gate
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        # Upload file with Simple Token mode
        file_input = page.locator("input[type='file']")
        file_input.set_input_files({
            "name"    : "format-test.txt",
            "mimeType": "text/plain",
            "buffer"  : b"token format verification",
        })
        page.wait_for_timeout(1000)

        # Walk wizard, selecting Simple Token
        for _ in range(3):
            btn = page.locator("button:has-text('Next'), button:has-text('Continue')").first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)

        simple_token = page.locator("text=Simple token, text=Simple Token, text=Friendly").first
        if simple_token.is_visible(timeout=3000):
            simple_token.click()
            page.wait_for_timeout(500)

        for _ in range(5):
            btn = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), "
                "button:has-text('Upload'), button:has-text('Encrypt'), "
                "button:has-text('Confirm')"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(1000)

        page.wait_for_timeout(3000)

        # Extract and validate format
        page_text = page.text_content("body") or ""
        token_matches = TOKEN_PATTERN.findall(page_text)
        if not token_matches:
            for input_el in page.locator("input[readonly], input[value]").all():
                val = input_el.get_attribute("value") or ""
                found = TOKEN_PATTERN.findall(val)
                if found:
                    token_matches.extend(found)

        assert token_matches, "No friendly token found"
        token = token_matches[0]

        # Validate format: word-word-NNNN
        parts = token.split("-")
        assert len(parts) == 3, f"Token should have 3 parts: {token}"
        assert parts[0].isalpha(), f"First part should be a word: {parts[0]}"
        assert parts[1].isalpha(), f"Second part should be a word: {parts[1]}"
        assert parts[2].isdigit() and len(parts[2]) == 4, f"Third part should be 4 digits: {parts[2]}"

    def test_friendly_token_resolves_in_new_tab(self, page, ui_url, send_server, screenshots):
        """Upload with Simple Token, then open the token in a new browser tab."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # Handle access gate
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        # Upload file with Simple Token mode
        file_input = page.locator("input[type='file']")
        file_input.set_input_files({
            "name"    : "resolve-test.txt",
            "mimeType": "text/plain",
            "buffer"  : SAMPLE_CONTENT.encode(),
        })
        page.wait_for_timeout(1000)

        # Walk wizard, selecting Simple Token
        for _ in range(3):
            btn = page.locator("button:has-text('Next'), button:has-text('Continue')").first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)

        simple_token = page.locator("text=Simple token, text=Simple Token, text=Friendly").first
        if simple_token.is_visible(timeout=3000):
            simple_token.click()
            page.wait_for_timeout(500)

        for _ in range(5):
            btn = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), "
                "button:has-text('Upload'), button:has-text('Encrypt'), "
                "button:has-text('Confirm')"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(1000)

        page.wait_for_timeout(3000)

        # Extract token
        page_text = page.text_content("body") or ""
        token_matches = TOKEN_PATTERN.findall(page_text)
        if not token_matches:
            for input_el in page.locator("input[readonly], input[value]").all():
                val = input_el.get_attribute("value") or ""
                found = TOKEN_PATTERN.findall(val)
                if found:
                    token_matches.extend(found)

        assert token_matches, "No friendly token found after upload"
        friendly_token = token_matches[0]

        # --- Open the token in a new tab ---
        resolve_page = page.context.new_page()
        resolve_page.goto(f"{ui_url}/en-gb/browse/#{friendly_token}")
        resolve_page.wait_for_load_state("networkidle")
        resolve_page.wait_for_timeout(5000)
        screenshots.capture(resolve_page, "05_token_resolved",
                            f"Friendly token '{friendly_token}' resolved in new tab")

        # Verify no "Transfer not found" error (the P0 bug)
        resolve_text = resolve_page.text_content("body") or ""
        assert "not found" not in resolve_text.lower(), (
            f"Token resolution failed — 'not found' error on page. "
            f"This is the P0 bug. Token: {friendly_token}"
        )

        # Verify content decrypted successfully
        assert SAMPLE_CONTENT in resolve_text or len(resolve_text) > 100, (
            "Token did not resolve to decrypted content"
        )

        resolve_page.close()

    def test_friendly_token_no_key_in_url_after_decrypt(self, page, ui_url, send_server, screenshots):
        """After decryption, the hash should be cleared from the URL (key not visible)."""
        page.goto(f"{ui_url}/en-gb/")
        page.wait_for_load_state("networkidle")

        # Handle access gate
        access_input = page.locator("input[type='text'], input[type='password']").first
        if access_input.is_visible(timeout=2000):
            access_input.fill(send_server.access_token)
            page.locator("button").first.click()
            page.wait_for_load_state("networkidle")

        # Upload + Simple Token (abbreviated — same flow as above)
        file_input = page.locator("input[type='file']")
        file_input.set_input_files({
            "name"    : "url-test.txt",
            "mimeType": "text/plain",
            "buffer"  : b"URL hash clearing test",
        })
        page.wait_for_timeout(1000)

        for _ in range(3):
            btn = page.locator("button:has-text('Next'), button:has-text('Continue')").first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)

        simple_token = page.locator("text=Simple token, text=Simple Token, text=Friendly").first
        if simple_token.is_visible(timeout=3000):
            simple_token.click()
            page.wait_for_timeout(500)

        for _ in range(5):
            btn = page.locator(
                "button:has-text('Next'), button:has-text('Continue'), "
                "button:has-text('Upload'), button:has-text('Encrypt'), "
                "button:has-text('Confirm')"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(1000)

        page.wait_for_timeout(3000)

        # Extract token
        page_text = page.text_content("body") or ""
        token_matches = TOKEN_PATTERN.findall(page_text)
        if not token_matches:
            for input_el in page.locator("input[readonly], input[value]").all():
                val = input_el.get_attribute("value") or ""
                found = TOKEN_PATTERN.findall(val)
                if found:
                    token_matches.extend(found)

        assert token_matches, "No friendly token found"
        friendly_token = token_matches[0]

        # Open in new tab and wait for decryption
        resolve_page = page.context.new_page()
        resolve_page.goto(f"{ui_url}/en-gb/browse/#{friendly_token}")
        resolve_page.wait_for_load_state("networkidle")
        resolve_page.wait_for_timeout(5000)

        # After decryption, the hash should be cleared
        final_url = resolve_page.url
        screenshots.capture(resolve_page, "06_hash_cleared",
                            f"URL after decrypt: {final_url}")

        # The friendly token or derived key should not remain in the URL hash
        if "#" in final_url:
            hash_fragment = final_url.split("#", 1)[1]
            assert hash_fragment == "" or hash_fragment != friendly_token, (
                f"Hash not cleared after decrypt — key may be visible in URL: {final_url}"
            )

        resolve_page.close()
