# QA Smoke Report

**Date:** 2026-03-29 02:16 UTC
**Version:** v0.2.41
**Target:** https://send.sgraph.ai
**Token:** set (17 chars)

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| Live smoke (7) | 6 | 1 | ❌ |

## Overall: FAIL

## Failures

### upload_wizard — HTTP 403

`GET https://send.sgraph.ai/en-gb/send/` returned **HTTP 403 Forbidden**.

All other routes (root, download, gallery, browse, viewer, invalid_hash) returned HTTP 200.

The access token (`SG_SEND_ACCESS_TOKEN=sg-send__team__qa`) was injected into
`localStorage` via `add_init_script` before any navigation. The 403 on `/en-gb/send/`
suggests the upload wizard route enforces server-side auth that the localStorage token
alone does not satisfy, or the token is invalid/expired for this route.

**Action required:** Investigate whether `/en-gb/send/` requires a different auth
mechanism, or whether the token needs to be sent as a request header rather than
stored in localStorage.

## Live Site Detail

```
Proxy: 21.0.0.25:15004
SG_SEND_ACCESS_TOKEN: set (17 chars)

=== LIVE SITE: 6/7 passed ===
  ✓ root: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/
  ✗ upload_wizard: FAIL — HTTP 403 · https://send.sgraph.ai/en-gb/send/
  ✓ download_entry: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/
  ✓ gallery_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/gallery/
  ✓ browse_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/browse/
  ✓ viewer_route: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/view/
  ✓ invalid_hash: PASS — HTTP 200 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
```

## Environment Notes

- Python 3.12 venv: OK
- Playwright / Chromium: OK
- SG/Send reference clone: OK
- Import verification (`Setup OK`): OK
- Network: proxy (`21.0.0.25:15004`) with TLS interception — `ignore_https_errors=True` required for Playwright
