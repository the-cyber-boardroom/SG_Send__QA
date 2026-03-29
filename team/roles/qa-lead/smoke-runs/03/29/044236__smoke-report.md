# QA Smoke Report

**Date:** 2026-03-29 04:42 UTC
**Version:** v0.2.42
**Target:** https://send.sgraph.ai
**Token:** set (17 chars)

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| Upload+download round-trip (5) | 5 | 0 | ✅ |
| Live smoke (6)                 | 6 | 0 | ✅ |

## Overall: PASS

## Failures (if any)

None — all steps passed.

## Suite 1 Detail

```
=== SUITE 1 (upload+download): 5/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=b53c193f58a2…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✓ browser_decrypt: PASS — state='complete'
Suite1 exit: 0
```

## Live Site Detail

```
Proxy: 21.0.0.33:15004
SG_SEND_ACCESS_TOKEN: set (17 chars)

=== LIVE SITE: 6/6 passed ===
  ✓ root: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/
  ✓ download_entry: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/
  ✓ gallery_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/gallery/
  ✓ browse_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/browse/
  ✓ viewer_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/view/
  ✓ invalid_hash: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
Suite5 exit: 0
```
