# QA Smoke Report

**Date:** 2026-04-12 08:22 UTC
**Version:** v0.2.49
**Target:** https://send.sgraph.ai
**Token:** set

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| suite_1__upload_download.py | 5 | 0 | PASS |
| suite_2__download_views.py | 4 | 0 | PASS |
| suite_3__error_states.py | 1 | 1 | FAIL |
| suite_4__friendly_token.py | 2 | 0 | PASS |
| suite_5__live_smoke.py | 6 | 0 | PASS |

## Overall: FAIL

## Failures

### suite_3__error_states.py — `error_wrong_key`

**Step:** `error_wrong_key`
**Error:** `Page.wait_for_function: Timeout 15000ms exceeded.`

**What preceded it:** Suite 3 started fresh (separate process). The `error_bogus_hash` step later passed (state='error' correctly detected). The `error_wrong_key` step timed out waiting for the page to reach an error state after presenting a wrong decryption key for a valid token hash. The browser page did not transition to the expected error state within the 15-second timeout.

**Note:** Suite 1 (upload+download), Suite 2 (view modes), Suite 4 (friendly token), and Suite 5 (live smoke) all passed cleanly.

## Suite Output

### Suite 1 — upload_download

```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=bb1a7d16a424…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### Suite 2 — download_views

```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=3607ef9b32c3…
  ✓ browser_browse_view: PASS — HTTP 200, state='complete'
  ✓ browser_gallery_view: PASS — HTTP 200, state='complete'
  ✓ browser_viewer_view: PASS — HTTP 200, state='complete'
```

### Suite 3 — error_states

```
=== SUITE 3 (error states): 1/2 passed ===
  ✗ error_wrong_key: FAIL — Page.wait_for_function: Timeout 15000ms exceeded.
  ✓ error_bogus_hash: PASS — state='error' (correct — bogus hash rejected)
```

### Suite 4 — friendly_token

```
=== SUITE 4 (friendly token): 2/2 passed ===
  ✓ browser_upload_token_mode: PASS — token='clover-marsh-4907'
  ✓ browser_resolve_token: PASS — token='clover-marsh-4907', state='complete'
```

### Suite 5 — live_smoke

```
Proxy: 21.0.0.19:15004
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

All 6 live site routes returned HTTP 200. The site is reachable and responding correctly. Access token was set (17 chars). Proxy: 21.0.0.19:15004.
