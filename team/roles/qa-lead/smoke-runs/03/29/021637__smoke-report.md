# QA Smoke Report

**Date:** 2026-03-29 02:16 UTC
**Version:** v0.2.41
**Target:** https://send.sgraph.ai
**Token:** set (17 chars)

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| Live smoke (7) | 0 | 7 | ❌ |

## Overall: FAIL

## Failures

All 7 checks failed with **HTTP 407 Proxy Authentication Required**.

The test environment requires proxy authentication to reach `send.sgraph.ai`.
This is an infrastructure/network issue in the CI sandbox — not a defect in
SG/Send itself. The live site cannot be reached from this environment without
proxy credentials.

## Live Site Detail

```
SG_SEND_ACCESS_TOKEN: set (17 chars)

=== LIVE SITE: 0/7 passed ===
  ✗ root: FAIL — HTTP 407 · https://send.sgraph.ai/
  ✗ upload_wizard: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/send/
  ✗ download_entry: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/download/
  ✗ gallery_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/gallery/
  ✗ browse_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/browse/
  ✗ viewer_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/view/
  ✗ invalid_hash: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
```

## Environment Notes

- Python 3.12 venv: OK
- Playwright / Chromium: installed successfully
- SG/Send reference clone: OK
- Import verification (`Setup OK`): passed
- Network: **BLOCKED** — HTTP 407 on all outbound requests to send.sgraph.ai
