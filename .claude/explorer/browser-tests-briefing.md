# Browser Tests Briefing — Phased Rollout

**Date:** 2026-03-23
**Branch:** `claude/create-qa-explorer-team-NUOoS`
**Context:** We have 48 API/httpx tests passing. We have ~60 Playwright browser tests
written but not yet verified against the local stack. This doc is the plan to
get them running phase by phase.

---

## What Already Exists

### Two parallel test layers (by design)

```
tests/qa/v030/
│
├── API / httpx tests (48 passing, no browser needed)
│   ├── test__transfer_helper.py   22 tests — AES-256-GCM crypto unit tests
│   ├── test__api_smoke.py         21 tests — create/upload/complete/download/info
│   └── test__zero_knowledge.py    5 tests  — server never sees plaintext
│
└── Playwright / browser tests (written, Chromium needed)
    ├── test__upload__single_file.py   4 tests  @p0 — upload wizard, footer version
    ├── test__combined_link.py         2 tests  @p0 — upload → combined link → auto-decrypt
    ├── test__separate_key.py          3 tests  @p0 — separate key mode, wrong key error
    ├── test__friendly_token.py        4 tests  @p0 — word-word-NNNN token mode
    ├── test__access_gate.py           4 tests  @p1 — token gate UI
    ├── test__manual_entry.py          5 tests  @p1 — manual transfer ID entry form
    ├── test__navigation.py            8 tests  @p1 — route handling (/browse, /gallery, /v)
    ├── test__download__browse.py      6 tests  @p1 — browse view, tabs, keyboard nav
    ├── test__download__gallery.py     6 tests  @p1 — gallery view, lightbox, controls
    ├── test__download__viewer.py      7 tests  @p1 — single file viewer, markdown
    ├── test__upload__folder.py        4 tests  @p1 — zip upload, gallery/browse auto-select
    └── test__pdf_present.py           7 tests  @p2 — PDF lightbox, keyboard shortcuts
```

### How the browser stack works

```
pytest
  └── send_server fixture          → in-memory FastAPI (dev branch, random port)
  └── ui_server fixture            → python -m http.server on localhost:10062
        _build_ui_serve_dir()        copies sgraph_ai_app_send__ui__user/v0/v0.3/v0.3.0/
                                     injects build-info.js → send_server.server_url
  └── browser fixture              → headless Chromium
  └── browser_context fixture      → base_url = http://localhost:10062
  └── page fixture                 → fresh page per test
```

**Critical:** UI server must bind to `localhost` (not `127.0.0.1`) — Web Crypto
API requires a secure context. `localhost` qualifies; `127.0.0.1` does not in
all Chromium configurations.

---

## What a "Browser Equivalent" Means

Each API test has a browser counterpart that exercises the same behaviour
through the actual UI instead of direct HTTP calls:

| API test | Browser equivalent |
|----------|-------------------|
| `test_create_returns_transfer_id` | Upload zone visible → file selected → wizard starts |
| `test_upload_succeeds` | File attached → wizard step transitions without error |
| `test_complete_succeeds` | Wizard reaches "Done" step → download link present |
| `test_download_returns_exact_bytes` | Open download link → content matches original |
| `test_info_does_not_expose_plaintext` | Server response in browser network tab has no plaintext |
| `test_server_stores_only_ciphertext` | Combined link works → manually entered wrong key fails |

The browser tests go further — they also verify UI state, step labels,
button text, loading states, and screenshot documentation.

---

## Phased Rollout

### Phase 1 — Prove the stack (1 test)

**Goal:** Confirm that `send_server → ui_server → browser → page` all chain
correctly on this machine/CI. One test, maximum signal.

**Test to run first:**

```bash
python -m pytest "tests/qa/v030/test__upload__single_file.py::TestSingleFileUpload::test_footer_version" -v --tb=long
```

**What it does:**
1. Starts in-memory API server
2. Builds and starts UI static server
3. Launches headless Chromium
4. Navigates to `http://localhost:10062/en-gb/`
5. Handles the access gate if present (enters token)
6. Reads `body` text content
7. Asserts `"v0.3.0"` appears (from the footer `v0.16.45 · UI v0.3.0`)

**Why this test:** It touches every layer of the stack (API → UI server → browser)
but doesn't require file upload, crypto, or complex UI interaction. If this passes,
the stack is wired correctly.

**Expected failure mode:** The footer shows a different version string than `v0.3.0`.
This is itself a useful QA signal — it means the installed UI package doesn't
match what the test expects.

---

### Phase 2 — Core upload flow (1 test)

**Goal:** Prove the browser can drive the 6-step upload wizard end to end.

**Test to run:**

```bash
python -m pytest "tests/qa/v030/test__upload__single_file.py::TestSingleFileUpload::test_single_file_upload_flow" -v --tb=long
```

**What it does:**
1. Navigates to upload page, handles access gate
2. Attaches a small text file via `page.set_input_files()`
3. Clicks through: Upload → Delivery → Share mode (Combined Link) → Confirm → Encrypt & Upload → Done
4. Extracts the download URL from the Done step
5. Opens download URL in a new browser tab
6. Waits for auto-decrypt
7. Asserts the original content is visible on screen
8. Captures 9 screenshots

**Why this test:** This is the core user journey — if this works, the fundamental
upload→encrypt→download loop is verified through the browser.

---

### Phase 3 — All P0 browser tests

Once Phases 1 and 2 pass, run the full P0 browser suite:

```bash
python -m pytest tests/qa/v030/ -m "p0" -v --tb=short
```

**P0 browser tests (13 total):**

| File | Tests | What they cover |
|------|-------|----------------|
| `test__upload__single_file.py` | 3 | Footer version, full upload flow, download link format |
| `test__combined_link.py` | 2 | Combined link mode, API-created transfer auto-decrypts |
| `test__separate_key.py` | 3 | Separate key mode, wrong key error, key not in URL |
| `test__friendly_token.py` | 4 | Simple token format, resolution, hash cleared after decrypt |

These are the deployment blockers — all must pass before promoting to main.

---

### Phase 4 — Full suite

```bash
python -m pytest tests/qa/v030/ -v
```

All ~102 tests. P1 failures require human sign-off but don't hard-block.

---

## What to Watch For (Known Issues)

### 1. Access gate behaviour
The access gate (token input) may or may not appear depending on whether the
in-memory server requires a token. The test server always requires
`send_server.access_token` via `x-sgraph-access-token` header.

The browser sends tokens differently — it stores the token in a component's
internal state after the user types it in, then includes it in API requests.
The gate test (`test__access_gate.py`) covers this specifically.

### 2. `networkidle` timing
Several tests use `page.wait_for_load_state("networkidle")` after navigation.
The in-memory server responds fast — if components make no further requests,
`networkidle` resolves immediately. If a test hangs here, add a fallback
`page.wait_for_timeout(2000)`.

### 3. Wrong `upload_url` in API response
**Known SG/Send bug:** `POST /api/transfers/create` returns
`"upload_url": "/transfers/upload/{id}"` (missing `/api/` prefix — 404s).
The browser's JavaScript uses `/api/transfers/upload/{id}` directly, so this
doesn't affect browser tests. But it is a real bug worth filing.

### 4. Duplicate FastAPI Operation IDs
`Routes__Vault__Pointer.py` has duplicate operation IDs — FastAPI logs warnings
on every startup. Not a test failure, but noise to be aware of.

### 5. Footer version string
The `build-info.js` injected by the test stack sets `appVersion: 'local-dev'`
and `uiVersion: 'v0.3.0'`. The footer component reads these and renders
`local-dev · UI v0.3.0`. The `test_footer_version` asserts `"v0.3.0"` which
matches. If the UI version in the installed package changes, update `UI_VERSION`
in `conftest.py`.

---

## How to Install Chromium

```bash
# In CI (has network access):
python -m playwright install --with-deps chromium

# Locally (if network available):
python -m playwright install chromium
```

The `--with-deps` flag also installs OS-level dependencies (libglib, libnss, etc.)
needed on Ubuntu/Debian CI runners.

---

## Screenshot Output

Browser tests save screenshots to:
```
sg_send_qa__site/pages/use-cases/{test_name}/screenshots/
    01_{description}.png
    02_{description}.png
    ...
    _metadata.json
```

These are the living documentation output — the reason every browser test
captures a screenshot at each significant step.
