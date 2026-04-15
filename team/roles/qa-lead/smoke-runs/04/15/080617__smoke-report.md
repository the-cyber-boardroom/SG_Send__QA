# QA Smoke Report

**Date:** 2026-04-15 08:06 UTC
**Version:** v0.2.49
**Target:** https://send.sgraph.ai
**Token:** set

## Results

| Suite | Passed | Failed | Status |
|-------|--------|--------|--------|
| suite_1__upload_download | 4 | 1 | FAIL |
| suite_2__download_views | 1 | 3 | FAIL |
| suite_3__error_states | 1 | 1 | FAIL |
| suite_4__friendly_token | 2 | 0 | PASS |
| suite_5__live_smoke | 6 | 0 | PASS |

## Overall: FAIL

## Failures

### suite_1__upload_download — browser_decrypt: FAIL

**Step:** `browser_decrypt`
**Error:** `state=None, body[:150]=DNS cache overflow`

**Preceding steps that passed:**
- `api_reachable`: HTTP 200
- `api_auth_and_create`: HTTP 200 — tid=bd54f4e1103d…
- `api_encrypt_upload`: HTTP 200 — 122 bytes uploaded
- `api_complete`: HTTP 200

The API upload/complete flow succeeded fully; the browser step failed to resolve
the local test server DNS — "DNS cache overflow" indicates the Playwright browser
could not reach the local test server URL.

---

### suite_2__download_views — browser_browse_view / browser_gallery_view / browser_viewer_view: FAIL

**Step:** `browser_browse_view`, `browser_gallery_view`, `browser_viewer_view`
**Error:** HTTP 503 for all three browser view steps

**Preceding step that passed:**
- `api_upload`: PASS — tid=9a5d276a98b7…

The upload API succeeded, but all three browser-based view modes returned HTTP 503,
indicating the local test server is returning a Service Unavailable response for
view routes during this run.

---

### suite_3__error_states — error_wrong_key: FAIL

**Step:** `error_wrong_key`
**Error:** HTTP 503

**Preceding step that passed:**
- `error_bogus_hash`: PASS — state='error' (correct — bogus hash rejected)

The wrong-key error-state test received HTTP 503 from the local test server,
consistent with the 503 pattern seen in suite 2.

---

### Common pattern across suites 1–3

Suites 1–3 all fail on browser/local-server steps. Suite 1's browser step
gets "DNS cache overflow"; suites 2–3 get HTTP 503. Both symptoms point to
the local test server (Playwright-driven local SG/Send instance) being
unreachable or failing to start correctly in this CI environment. The live
site (suite 5) is fully healthy, ruling out any production-side issue.

## Suite Output

### suite_1__upload_download
```
=== SUITE 1 (upload+download): 4/5 passed ===
  ✓ api_reachable: PASS — HTTP 200
  ✓ api_auth_and_create: PASS — HTTP 200 — tid=bd54f4e1103d…
  ✓ api_encrypt_upload: PASS — HTTP 200 — 122 bytes uploaded
  ✓ api_complete: PASS — HTTP 200
  ✗ browser_decrypt: FAIL — state=None, body[:150]=DNS cache overflow
```

### suite_2__download_views
```
=== SUITE 2 (view modes): 1/4 passed ===
  ✓ api_upload: PASS — tid=9a5d276a98b7…
  ✗ browser_browse_view: FAIL — HTTP 503
  ✗ browser_gallery_view: FAIL — HTTP 503
  ✗ browser_viewer_view: FAIL — HTTP 503
```

### suite_3__error_states
```
=== SUITE 3 (error states): 1/2 passed ===
  ✗ error_wrong_key: FAIL — HTTP 503
  ✓ error_bogus_hash: PASS — state='error' (correct — bogus hash rejected)
```

### suite_4__friendly_token
```
=== SUITE 4 (friendly token): 2/2 passed ===
  ✓ browser_upload_token_mode: PASS — token='brook-judge-9539'
  ✓ browser_resolve_token: PASS — token='brook-judge-9539', state='complete'
```

### suite_5__live_smoke
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

All 6 live site checks passed. The production deployment at https://send.sgraph.ai
is healthy across all routes tested:
- Root (`/en-gb/`) — HTTP 200
- Download entry (`/en-gb/download/`) — HTTP 200
- Gallery route (`/en-gb/gallery/`) — HTTP 200
- Browse route (`/en-gb/browse/`) — HTTP 200
- Viewer route (`/en-gb/view/`) — HTTP 200
- Invalid hash (`/en-gb/download/#bogus123/fakekey==`) — HTTP 200 (client-side error handling)

Token was set (17 chars). No proxy configured.
