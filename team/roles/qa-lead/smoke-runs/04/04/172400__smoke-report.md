# QA Smoke Report

**Date:** 2026-04-04 17:24 UTC
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

### suite_3__error_states.py — `error_wrong_key`

**Step failed:** `error_wrong_key`

**Error:**
```
✗ error_wrong_key: FAIL — Page.wait_for_function: Timeout 15000ms exceeded.
```

**Context:** The test uploads a file with a known key, then attempts to decrypt it using a deliberately wrong key. The browser state was expected to transition to `'error'` within 15 s, but the page did not reach that state before the timeout. The preceding step (`error_bogus_hash`) passed correctly — a bogus hash was rejected with state `'error'` as expected.

**Passing step in the same suite:**
```
✓ error_bogus_hash: PASS — state='error' (correct — bogus hash rejected)
```

---

## Suite Output

### suite_1__upload_download.py
```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=93820d55cf1f…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### suite_2__download_views.py
```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=a49d1820418f…
  ✓ browser_browse_view: PASS — HTTP 200, state='complete'
  ✓ browser_gallery_view: PASS — HTTP 200, state='complete'
  ✓ browser_viewer_view: PASS — HTTP 200, state='complete'
```

### suite_3__error_states.py
```
=== SUITE 3 (error states): 1/2 passed ===
  ✗ error_wrong_key: FAIL — Page.wait_for_function: Timeout 15000ms exceeded.
  ✓ error_bogus_hash: PASS — state='error' (correct — bogus hash rejected)
```

### suite_4__friendly_token.py
```
=== SUITE 4 (friendly token): 2/2 passed ===
  ✓ browser_upload_token_mode: PASS — token='humor-match-4697'
  ✓ browser_resolve_token: PASS — token='humor-match-4697', state='complete'
```

### suite_5__live_smoke.py
```
=== SUITE 5 (live smoke): 6/6 passed ===
  ✓ root: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/
  ✓ download_entry: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/
  ✓ gallery_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/gallery/
  ✓ browse_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/browse/
  ✓ viewer_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/view/
  ✓ invalid_hash: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
```

## Live Site Detail

Proxy: 21.0.0.89:15004
SG_SEND_ACCESS_TOKEN: set (17 chars)

All 6 live-site HTTP probes returned HTTP 200. All routes reachable.
