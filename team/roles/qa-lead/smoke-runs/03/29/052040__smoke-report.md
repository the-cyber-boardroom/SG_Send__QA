# QA Smoke Report

**Date:** 2026-03-29 05:20 UTC
**Version:** v0.2.42
**Target:** https://send.sgraph.ai
**Token:** set

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| suite_1__upload_download.py | 5 | 0 | PASS |
| suite_2__download_views.py | 4 | 0 | PASS |
| suite_5__live_smoke.py | 6 | 0 | PASS |

## Overall: PASS

## Failures (if any)

None.

## Suite Output

### suite_1__upload_download.py

```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=c1ec37fc4bca…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
```

### suite_2__download_views.py

```
=== SUITE 2 (view modes): 4/4 passed ===
  ✓ api_upload: PASS — tid=e801bf26e21c…
  ✓ browser_browse_view: PASS — HTTP 200, state='complete'
  ✓ browser_gallery_view: PASS — HTTP 200, state='complete'
  ✓ browser_viewer_view: PASS — HTTP 200, state='complete'
```

### suite_5__live_smoke.py

```
Proxy: 21.0.0.99:15004
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

All 6 live site checks passed (HTTP 200). Routes tested: root, download entry,
gallery, browse, viewer, and invalid-hash graceful handling.
