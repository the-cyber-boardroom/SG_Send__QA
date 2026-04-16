# QA Smoke Report

**Date:** 2026-04-16 08:16 UTC
**Version:** v0.2.49
**Target:** https://send.sgraph.ai
**Token:** set

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| suite_1__upload_download.py | 4 | 1 | FAIL |
| suite_2__download_views.py | 4 | 0 | PASS |
| suite_3__error_states.py | 1 | 1 | FAIL |
| suite_4__friendly_token.py | 2 | 0 | PASS |
| suite_5__live_smoke.py | 6 | 0 | PASS |

## Overall: FAIL

## Failures

### Suite 1 — `browser_decrypt`
- **Error:** `state=None, body[:150]=DNS cache overflow`
- **Step failed:** Browser decryption step — Playwright page load after completing upload cycle
- **Preceding steps:** api_reachable ✓, api_auth_and_create ✓ (tid=030e1799db87…), api_encrypt_upload ✓ (122 bytes), api_complete ✓
- **Root cause signal:** DNS cache overflow on the local test server's hostname resolution — browser could not resolve the local server address to decrypt the uploaded file.

### Suite 3 — `error_wrong_key`
- **Error:** `Page.wait_for_function: Timeout 15000ms exceeded.`
- **Step failed:** Browser wait for error state after presenting wrong decryption key
- **Preceding steps:** error_bogus_hash ✓ (bogus hash correctly rejected with state='error')
- **Root cause signal:** The page did not reach the expected error state within 15 s when given a valid hash but wrong key — UI may not be surfacing the decryption failure state, or the wrong-key error path is timing out.

## Suite Output

### Suite 1 (upload+download)

```
=== SUITE 1 (upload+download): 4/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=030e1799db87…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✗ browser_decrypt: FAIL — state=None, body[:150]=DNS cache overflow
```

### Suite 2 (download views)

```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=f719958ad2e5…
  ✓ browser_browse_view: PASS — HTTP 200, state='complete'
  ✓ browser_gallery_view: PASS — HTTP 200, state='complete'
  ✓ browser_viewer_view: PASS — HTTP 200, state='complete'
```

### Suite 3 (error states)

```
=== SUITE 3 (error states): 1/2 passed ===
  ✗ error_wrong_key: FAIL — Page.wait_for_function: Timeout 15000ms exceeded.
  ✓ error_bogus_hash: PASS — state='error' (correct — bogus hash rejected)
```

### Suite 4 (friendly token)

```
=== SUITE 4 (friendly token): 2/2 passed ===
  ✓ browser_upload_token_mode: PASS — token='mount-toast-4521'
  ✓ browser_resolve_token: PASS — token='mount-toast-4521', state='complete'
```

### Suite 5 (live smoke)

```
No proxy configured
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

All 6 live site routes returned HTTP 200. Token set (17 chars). Production instance healthy.
