# QA Smoke Report

**Date:** 2026-04-03 08:31 UTC
**Version:** v0.2.47
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

### Suite 3 — error_wrong_key

**Step:** `error_wrong_key`
**Error:** `Page.wait_for_function: Timeout 15000ms exceeded.`
**What preceded it:** The step uploaded a file and navigated to the download page with a deliberately wrong decryption key, then waited for the page's JS state to transition to `'error'`. The wait timed out after 15 000 ms — the page did not surface the expected error state within the timeout window.
**Passing context:** The companion step `error_bogus_hash` passed — the page correctly returned `state='error'` when given a non-existent hash. Only the wrong-key path timed out, suggesting the client-side decryption error path may not be setting the expected state flag, or is doing so more slowly than 15 s.

## Suite Output

### Suite 1 — upload+download (5/5 PASS)

```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=1e8521656c77…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### Suite 2 — view modes (4/4 PASS)

```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=332336129232…
  ✓ browser_browse_view: PASS — HTTP 200, state='complete'
  ✓ browser_gallery_view: PASS — HTTP 200, state='complete'
  ✓ browser_viewer_view: PASS — HTTP 200, state='complete'
```

### Suite 3 — error states (1/2 FAIL)

```
=== SUITE 3 (error states): 1/2 passed ===
  ✗ error_wrong_key: FAIL — Page.wait_for_function: Timeout 15000ms exceeded.
  ✓ error_bogus_hash: PASS — state='error' (correct — bogus hash rejected)
```

### Suite 4 — friendly token (2/2 PASS)

```
=== SUITE 4 (friendly token): 2/2 passed ===
  ✓ browser_upload_token_mode: PASS — token='grape-bread-4669'
  ✓ browser_resolve_token: PASS — token='grape-bread-4669', state='complete'
```

### Suite 5 — live smoke (6/6 PASS)

```
Proxy: 21.0.0.197:15004
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

All 6 live-site routes returned HTTP 200. Access token was present (17 chars). Proxy routed through 21.0.0.197:15004. No live-site failures detected.
