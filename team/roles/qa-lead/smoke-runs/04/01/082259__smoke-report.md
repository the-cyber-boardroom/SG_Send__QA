# QA Smoke Report

**Date:** 2026-04-01 08:22 UTC
**Version:** v0.2.47
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

### suite_3__error_states — error_wrong_key

**Step:** `error_wrong_key`
**Error:** `Page.wait_for_function: Timeout 15000ms exceeded.`
**Description:** The test uploaded a file and then attempted to decrypt it with a deliberately wrong key, expecting the page to enter an error state. The `wait_for_function` call timed out after 15 seconds, meaning the page never reached the expected error state within the timeout window.
**Preceding steps:** None — this was the first step in the suite.
**Note:** The second step (`error_bogus_hash`) passed correctly, confirming the local test server was operational.

## Suite Output

### Suite 1 — upload+download

```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=4068575b316c…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### Suite 2 — download views

```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=6d5c0769808b…
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
  ✓ browser_upload_token_mode: PASS — token='barn-apple-0706'
  ✓ browser_resolve_token: PASS — token='barn-apple-0706', state='complete'
```

### Suite 5 — live smoke

```
Proxy: 21.0.0.73:15004
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

All 6 live site checks passed. The production instance at `https://send.sgraph.ai` is reachable and returning HTTP 200 for all tested routes (root, download entry, gallery, browse, viewer, and invalid-hash error path).
