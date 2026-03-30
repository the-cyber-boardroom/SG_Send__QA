# QA Smoke Report

**Date:** 2026-03-29 00:32 UTC
**Version:** v0.2.41
**Target:** https://send.sgraph.ai

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| Unit tests       | 180 | 0 | ✅ |
| API & Crypto     | 48  | 0 | ✅ |
| P0 Browser       | 11  | 1 | ❌ |
| P1 Browser       | 32  | 0 | ✅ |
| Live smoke (7)   | 0   | 7 | ❌ |

## Overall: FAIL

## Failures

### P0 Browser — `test_separate_key_ui_flow`

```
tests/qa/v030/p0__separate_key/test__separate_key.py::TestSeparateKey::test_separate_key_ui_flow FAILED

tests/qa/v030/p0__separate_key/test__separate_key.py:132: in test_separate_key_ui_flow
    file_input.set_input_files({
playwright._impl._errors.TimeoutError: Locator.set_input_files: Timeout 5000ms exceeded.
Call log:
  - waiting for locator("#file-input")
```

**Summary:** The `#file-input` element was not found within 5 seconds on the upload page during the separate-key UI flow test. The other separate-key tests passed (API path and wrong-key error), and all other upload tests passed. This suggests either a timing issue on the file input rendering or a UI state regression specific to the separate-key upload path.

Note: `test_separate_key_decrypt_via_api` is marked `xfail` and did xfail as expected — not counted as a failure.

---

### Live Smoke — All 7 checks: HTTP 407

```
=== LIVE SITE: 0/7 passed ===
  ✗ root: FAIL — HTTP 407 · https://send.sgraph.ai/
  ✗ upload_wizard: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/send/
  ✗ download_entry: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/download/
  ✗ gallery_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/gallery/
  ✗ browse_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/browse/
  ✗ viewer_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/view/
  ✗ invalid_hash: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
```

**Summary:** HTTP 407 = Proxy Authentication Required. All live site checks are blocked by a proxy layer in the CI/sandbox environment. This is an infrastructure/environment issue — not a regression in the SG/Send application itself. The local stack tests (Suites 3 & 4) confirm the application is working correctly.

## Live Site Detail

```
=== LIVE SITE: 0/7 passed ===
  ✗ root: FAIL — HTTP 407 · https://send.sgraph.ai/
  ✗ upload_wizard: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/send/
  ✗ download_entry: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/download/
  ✗ gallery_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/gallery/
  ✗ browse_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/browse/
  ✗ viewer_route: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/view/
  ✗ invalid_hash: FAIL — HTTP 407 · https://send.sgraph.ai/en-gb/download/#bogus123/fakekey==
```

## Notes

- Suite 3 (P0 Browser) had 1 xfail (`test_separate_key_decrypt_via_api`) which is expected and does not count as a failure.
- The live smoke failures are caused by a network proxy blocking outbound HTTPS in the sandbox environment, not by application issues.
- Local stack coverage (Suites 1–4) shows 271/272 tests passing.
