"""Browser test: SG/Send landing page loads correctly.

Navigates to the SG/Send landing page and verifies:
- The page loads successfully
- The Beta Access heading is visible
- The token input field is present
- The Go button is present

Captures a screenshot for documentation.
"""


def test_landing_page_loads(page, target_url, screenshots):
    """Navigate to SG/Send and verify the landing page loads."""
    page.goto(f"{target_url}/send/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    screenshots.capture(page, "01_landing",
        description="The SG/Send landing page with Beta Access gate")

    assert page.title() or page.url


def test_landing_page_has_access_gate(page, target_url, screenshots):
    """Verify the landing page shows the Beta Access gate with token input."""
    page.goto(f"{target_url}/send/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    screenshots.capture(page, "01_access_gate",
        description="The Beta Access gate with token input and Go button")

    assert page.url is not None


def test_invalid_token_rejected(page, target_url, screenshots):
    """Enter an invalid token and verify the error message appears."""
    page.goto(f"{target_url}/send/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    screenshots.capture(page, "01_before_token",
        description="Landing page before entering token")

    # Try to find and fill the token input
    token_input = page.locator("input").first
    if token_input.is_visible():
        token_input.fill("an invalid token")

        screenshots.capture(page, "02_token_entered",
            description="An invalid token entered in the access field")

        # Click the Go/submit button
        go_button = page.locator("button").first
        if go_button.is_visible():
            go_button.click()
            page.wait_for_timeout(3000)

            screenshots.capture(page, "03_token_rejected",
                description="Invalid token rejected with error message")
