---
title: "Known Bug: Separate-key decrypt — content not visible in body"
permalink: /pages/known-bugs/separate_key_decrypt_content/
---

# Known Bug: Separate-key decrypt — content not visible in body

**Priority:** P0
**Status:** Open
**Test:** `tests/qa/v030/p0__separate_key/test__separate_key.py::TestSeparateKey::test_separate_key_decrypt_via_api`
**Marked:** `@pytest.mark.xfail(strict=True)` — runs every CI pass, expected to fail

---

## What Should Happen

1. A transfer is created via API with Separate Key share mode
2. The download link is opened **without** the key in the hash
3. The user sees a key input field and enters the correct key
4. Clicking **Decrypt** decrypts the file and shows the content inline on the page
5. `page.text_content("body")` contains the decrypted file text

## What Actually Happens

After clicking Decrypt and waiting 5 seconds, the decrypted content is **not found in the page body text**. The body contains only the shell of the download page (navigation, language switcher, JS bootstrap code) — the file content is absent.

The page does not error. It appears to complete "something" — but the content is not accessible via `page.text_content("body")`.

---

## Likely Root Cause

SG/Send's download viewer probably renders decrypted content inside a **Web Component / shadow DOM** or triggers a **browser download** rather than displaying content inline. Either of these would make the text invisible to `page.text_content("body")`.

The test assertion strategy (`assert content in body_text`) is correct for an inline viewer but breaks if the render target is:

- A shadow root (needs `page.evaluate("document.querySelector('...').shadowRoot.textContent")`)
- A `<iframe>` (needs frame switching)
- A triggered `Blob` download (needs `page.expect_download()`)

---

## Screenshots

Screenshots below are captured automatically by the test during each CI run. They show the state of the page at each step — the failure is visible at step 4 where the page does not show the decrypted content.

### 01 — Ready state (key input visible)

The download page loaded with the transfer ID in the hash but no key. The key input should be visible here.

![Ready state — key input visible](screenshots/01_ready_state.png)

### 02 — Transfer info

The page before key entry. Should show transfer metadata (size, upload time).

![Transfer info displayed](screenshots/02_transfer_info.png)

### 03 — Key entered

The correct base64 key has been filled into the key input field.

![Encryption key entered](screenshots/03_key_entered.png)

### 04 — After decrypt click (the bug)

**This is where the bug is.** Five seconds after clicking Decrypt, the page does not show the file content. The assertion `assert "Separate key test — UC-05." in body_text` fails here.

![State after decrypt — content not visible](screenshots/04_decrypted.png)

---

## Assertion That Fails

```python
body_text = page.text_content("body") or ""
assert SAMPLE_CONTENT in body_text, (
    f"Content not found after decryption. Transfer ID: {tid}"
)
```

`SAMPLE_CONTENT = "Separate key test — UC-05."`

---

## How to Fix the Test

Once the rendering mechanism is confirmed, update the assertion to match. Options:

**If content is in a shadow DOM element:**
```python
content = page.evaluate("document.querySelector('send-viewer').shadowRoot.textContent")
assert SAMPLE_CONTENT in content
```

**If a download is triggered:**
```python
with page.expect_download() as dl:
    decrypt_btn.click()
download = dl.value
# read the downloaded file and assert content
```

**If content is in an iframe:**
```python
frame = page.frame_locator("iframe").first
content = frame.locator("body").text_content()
assert SAMPLE_CONTENT in content
```

---

## How to Retire This Bug

1. Identify the actual render mechanism by inspecting the live page after decrypt
2. Update the assertion in `test_separate_key_decrypt_via_api`
3. Remove the `@pytest.mark.xfail` decorator
4. Confirm the test goes green in CI
5. Delete this known-bug page (or move it to an `archived/` subfolder)
