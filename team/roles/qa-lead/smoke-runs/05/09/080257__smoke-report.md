# QA Smoke Report

**Date:** 2026-05-09 08:02 UTC
**Version:** v0.2.51
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

**Preceding steps in suite 3:** None — this was the first step to run, and it failed. The second step (`error_bogus_hash`) passed.

**What the test does:** Uploads a file with one key, then attempts to decrypt it in the browser with a *wrong* key. The test then waits for the page to reach an `error` state (via `wait_for_function`). The timeout indicates the page did not transition to an error state within 15 seconds — the UI may have silently stalled, shown an unexpected state, or the decryption error handling did not render the expected error state element.

**No speculation beyond output:** The script's exit code was 1; no further details were emitted.

## Suite Output

### Suite 1 — upload+download (5/5 PASS)

```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=fda6ba3420f3…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### Suite 2 — view modes (4/4 PASS)

```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=8b8b03269c80…
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
  ✓ browser_upload_token_mode: PASS — token='pepper-fiber-6647'
  ✓ browser_resolve_token: PASS — token='pepper-fiber-6647', state='complete'
```

### Suite 5 — live smoke (6/6 PASS)

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

All 6 live site checks passed. The production instance at `https://send.sgraph.ai` is reachable and all primary routes return HTTP 200. Invalid-hash handling also returns HTTP 200 (client-side error handling confirmed).
