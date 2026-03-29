# QA Smoke Report

**Date:** 2026-03-29 03:55 UTC
**Version:** v0.2.42
**Target:** https://send.sgraph.ai
**Token:** set

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| Upload+download round-trip (2) | 0 | 1 | ❌ |
| Live smoke (6)                 | 6 | 0 | ✅ |

## Overall: FAIL

## Failures (if any)

### api_upload — FAIL
```
The read operation timed out
```

**Note:** `QA_Transfer_Helper` does not accept a `timeout` parameter (attribute assignment blocked by type-safe init). The upload HTTP request itself timed out connecting to `https://send.sgraph.ai`. The `browser_download_decrypt` test was skipped as a result (depends on a successful upload). Live site browser tests (Suite 5) all passed, confirming the site is reachable via the proxy — the upload API endpoint may be rate-limiting or the connection stalled during the multipart POST.

## Suite 1 Detail

```
=== SUITE 1 (upload+download): 0/1 passed ===
  ✗ api_upload: FAIL — The read operation timed out
Suite1 exit: 1
```

## Live Site Detail

```
Proxy: 21.0.0.57:15004
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
