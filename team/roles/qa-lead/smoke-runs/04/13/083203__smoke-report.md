# QA Smoke Report

**Date:** 2026-04-13 08:32 UTC
**Version:** v0.2.49
**Target:** https://send.sgraph.ai
**Token:** set

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| suite_1__upload_download | 5 | 0 | PASS |
| suite_2__download_views | 4 | 0 | PASS |
| suite_3__error_states | 1 | 1 | FAIL |
| suite_4__friendly_token | 2 | 0 | PASS |
| suite_5__live_smoke | 6 | 0 | PASS |

## Overall: FAIL

## Failures

### suite_3__error_states — `error_wrong_key`

**Step that failed:** `error_wrong_key`
**Error:** `Page.wait_for_function: Timeout 15000ms exceeded.`

**Preceding steps in suite:**
- No prior steps — this was the first test run in Suite 3.

**Context:** The test uploads a file, then attempts to open the download page with a deliberately wrong decryption key and waits for the page to enter an `'error'` state. The browser page never reached the error state within the 15-second timeout, indicating the client-side error-detection logic did not fire for a wrong-key scenario. The second test (`error_bogus_hash`) passed, confirming the test infrastructure itself is functional.

## Suite Output

### Suite 1 — upload_download (5/5 PASS)
```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=2aa7592ae9a7…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### Suite 2 — download_views (4/4 PASS)
```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=3e8d73c0306c…
  ✓ browser_browse_view: PASS — HTTP 200, state='complete'
  ✓ browser_gallery_view: PASS — HTTP 200, state='complete'
  ✓ browser_viewer_view: PASS — HTTP 200, state='complete'
```

### Suite 3 — error_states (1/2 FAIL)
```
=== SUITE 3 (error states): 1/2 passed ===
  ✗ error_wrong_key: FAIL — Page.wait_for_function: Timeout 15000ms exceeded.
  ✓ error_bogus_hash: PASS — state='error' (correct — bogus hash rejected)
```

### Suite 4 — friendly_token (2/2 PASS)
```
=== SUITE 4 (friendly token): 2/2 passed ===
  ✓ browser_upload_token_mode: PASS — token='float-toast-3643'
  ✓ browser_resolve_token: PASS — token='float-toast-3643', state='complete'
```

### Suite 5 — live_smoke (6/6 PASS)
```
Proxy: 21.0.0.157:15004
SG_SEND_ACCESS_TOKEN: set (17 chars)

=== LIVE SITE: 6/6 passed ===
  ✓ root: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/
  ✓ download_entry: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/
  ✓ gallery_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/gallery/
  ✓ browse_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/browse/
  ✓ viewer_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/view/
  ✓ invalid_hash: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
```

## Live Site Detail

All 6 live routes returned HTTP 200. Token was set (17 chars). Proxy used: `21.0.0.157:15004`.
