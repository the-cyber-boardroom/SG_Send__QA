# QA Smoke Report

**Date:** 2026-03-29 03:35 UTC
**Version:** v0.2.41
**Target:** https://send.sgraph.ai
**Token:** set

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| Upload+download round-trip (2) | 0 | 1 | ❌ |
| Live smoke (6)                 | 6 | 0 | ✅ |

## Overall: FAIL

## Failures

### api_upload — FAIL
```
The read operation timed out
```

Suite 1 (`api_upload`) failed with a network timeout when attempting to upload
via the SG/Send API. The token is present (17 chars) but the upload HTTP
request timed out. This is likely a transient network issue or the API is
rate-limiting/unavailable at the time of the run.

`browser_download_decrypt` was not attempted because the upload step failed to
produce a transfer ID.

## Suite 1 Detail

```
=== SUITE 1 (upload+download): 0/1 passed ===
  ✗ api_upload: FAIL — The read operation timed out
Suite1 exit: 1
```

## Live Site Detail

```
Proxy: 21.0.0.21:15004
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
