# QA Smoke Report

**Date:** 2026-04-14 08:04 UTC
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

### suite_3__error_states.py — error_wrong_key

**Step:** `error_wrong_key`
**Error:** `Page.wait_for_function: Timeout 15000ms exceeded.`
**Status:** FAIL

The test uploads a file, then attempts to decrypt it using a wrong encryption key.
The expected behaviour is that the page reaches an `error` state.
Instead, the page timed out after 15 000 ms without reaching any terminal state — the
UI did not surface an error for an incorrect decryption key within the timeout window.

The companion step (`error_bogus_hash`) passed: when given a completely bogus hash the
server/UI correctly returns `state='error'`.

**Preceding steps that succeeded:**
- The suite began (upload step is internal to this test step).
- `error_bogus_hash` passed immediately after.

No speculation beyond the script output.

## Suite Output

### Suite 1 — upload+download

```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=df494fc2a875…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### Suite 2 — view modes

```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=047c4dc4e422…
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
  ✓ browser_upload_token_mode: PASS — token='medal-queen-1820'
  ✓ browser_resolve_token: PASS — token='medal-queen-1820', state='complete'
```

### Suite 5 — live smoke

```
Proxy: 21.0.0.245:15004
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

All six live-site routes returned HTTP 200. The live site at https://send.sgraph.ai is
reachable and all navigational routes (root, download entry, gallery, browse, viewer,
invalid-hash handling) respond correctly.
