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

### api_upload — FAIL (root cause identified and fixed)

**Error:** `The read operation timed out`

**Root cause:** `QA_Transfer_Helper` uses `httpx.post()` for three API calls
(create → upload → complete). The `httpx` default timeout is **5 seconds**.
Through the Claude cloud egress proxy (`21.0.0.21:15004`), which performs TLS
interception, the upload round-trip consistently exceeds this limit.

Note: `curl` and Playwright are unaffected — curl reads proxy env vars
natively and Playwright has its own configured timeout. Only `httpx` was
silent about the proxy-induced latency.

**Fix applied:** Added `timeout: float = 30.0` field to `QA_Transfer_Helper`
and passed it to all three httpx calls (create, upload, complete). The
briefing now constructs the helper with `timeout=30.0` explicitly.

**Verified:** Suite 1 re-run after the fix passed 2/2 — `api_upload` PASS,
`browser_download_decrypt` PASS (`send-download.state = 'complete'`).

`browser_download_decrypt` was skipped in this run because the upload timed
out before producing a transfer ID.

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
