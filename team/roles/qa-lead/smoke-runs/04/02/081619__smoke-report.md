# QA Smoke Report

**Date:** 2026-04-02 08:16 UTC
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

## Failures (if any)

### suite_3__error_states.py — `error_wrong_key`

**Step failed:** `error_wrong_key`

**Error:**
```
Page.wait_for_function: Timeout 15000ms exceeded.
```

**What preceding steps showed:**
- Suite 3 ran 2 tests total.
- `error_bogus_hash` PASSED — a bogus hash was correctly rejected by the app with `state='error'`.
- `error_wrong_key` FAILED — the test uploaded a file and then attempted to decrypt it with the wrong key, waiting up to 15 000 ms for a JS condition (likely `state='error'`) that never became true within the timeout. The page did not transition to an error state when presented with an incorrect decryption key.

No speculation beyond the script output is included.

## Suite Output

### Suite 1 — upload+download

```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=29a77642585a…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### Suite 2 — view modes

```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=0b91a06652d0…
  ✓ browser_browse_view: PASS — HTTP 200, state='complete'
  ✓ browser_gallery_view: PASS — HTTP 200, state='complete'
  ✓ browser_viewer_view: PASS — HTTP 200, state='complete'
```

### Suite 3 — error states

```
=== SUITE 3 (error states): 1/2 passed ===
  ✗ error_wrong_key: FAIL — Page.wait_for_function: Timeout 15000ms exceeded.
  ✓ error_bogus_hash: PASS — state='error' (correct — bogus hash rejected)
```

### Suite 4 — friendly token

```
=== SUITE 4 (friendly token): 2/2 passed ===
  ✓ browser_upload_token_mode: PASS — token='stamp-relay-1955'
  ✓ browser_resolve_token: PASS — token='stamp-relay-1955', state='complete'
```

### Suite 5 — live smoke

```
Proxy: 21.0.0.113:15004
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

```
Proxy: 21.0.0.113:15004
SG_SEND_ACCESS_TOKEN: set (17 chars)

=== LIVE SITE: 6/6 passed ===
  ✓ root: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/
  ✓ download_entry: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/
  ✓ gallery_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/gallery/
  ✓ browse_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/browse/
  ✓ viewer_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/view/
  ✓ invalid_hash: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
```
