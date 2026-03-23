# Reference: Test Catalogue

**Maintained by:** Librarian
**Last updated:** 2026-03-23

---

## Overview

| Suite | Location | Files | Coverage |
|-------|----------|:-----:|----------|
| Unit | `tests/unit/` | 1 | QA project internals |
| Integration | `tests/integration/user/` | 1 | Browser smoke tests against production |
| v0.3.0 Acceptance | `tests/qa/v030/` | 12 | Full acceptance: API, crypto, browser, zero-knowledge |

---

## Unit Tests

### `tests/unit/utils/test_Version.py`

Tests the `Version` utility class that reads `sg_send_qa/version`.

---

## Integration Tests (Browser — Production)

### `tests/integration/user/test_landing_page.py`

Browser tests against the live SG/Send at `https://send.sgraph.ai`.

| Test | What it verifies | Screenshots |
|------|-----------------|:-----------:|
| `test_landing_page_loads` | Page loads, renders Beta Access UI | 1 |
| `test_landing_page_has_access_gate` | Token input + Go button visible | 1 |
| `test_invalid_token_rejected` | Invalid token → error feedback | 3 |

**Fixtures:** `tests/conftest.py` — browser setup, URL reachability check, target URL from env.

---

## v0.3.0 Acceptance Tests (Local Server)

### Infrastructure: `tests/qa/v030/conftest.py`

Spins up a complete local test environment:
- **`send_server`** — real SG/Send FastAPI on random port, in-memory storage
- **`ui_server`** — static HTML server on localhost:10062 with injected config
- **`transfer_helper`** — creates encrypted transfers via API (no browser)
- **Priority markers:** `@pytest.mark.p0` / `p1` / `p2` / `p3`

### Test Files

| File | Priority | What it tests | Key assertions |
|------|:--------:|---------------|----------------|
| `test__access_gate.py` | P1 | Token entry → upload zone visible | Access gate flow, UI state transition |
| `test__upload__single_file.py` | — | Single file upload through access gate | Full upload lifecycle |
| `test__upload__folder.py` | — | Folder upload through access gate | Multi-file upload |
| `test__combined_link.py` | — | Combined link access pattern | Link + key in same URL |
| `test__separate_key.py` | — | Separate key access pattern | Key delivered separately |
| `test__manual_entry.py` | P1 | Manual token entry flow | Hand-typed token acceptance |
| `test__friendly_token.py` | — | Friendly/memorable token flow | Human-readable token format |
| `test__download__browse.py` | — | Download with file browser view | Browse → select → download |
| `test__download__gallery.py` | — | Download with gallery view | Visual gallery → download |
| `test__download__viewer.py` | — | Download with file viewer | Preview → download |
| `test__navigation.py` | — | Navigation between upload/download | Tab switching, route handling |
| `test__zero_knowledge.py` | — | Zero-knowledge encryption properties | Server never sees plaintext, SGMETA envelope, key stays in fragment |

### Test Priority Gating (CI)

```
P0 (deployment blockers)  → Must pass or pipeline fails
P1 (sign-off required)    → If failing, flags for human review
P2 (bug filed)            → Informational
P3 (nice to have)         → Informational
```

---

## Configuration

| File | Purpose |
|------|---------|
| `tests/config/test-config.json` | Target URLs, screenshot viewport (1280×720), diff threshold (1%) |
| `tests/config/.env.example` | Environment variable template |

---

## How to Run

```bash
# Unit tests (fast, no dependencies)
python -m pytest tests/unit/ -v

# Integration tests (needs network, Chromium)
TEST_TARGET_URL=https://send.sgraph.ai python -m pytest tests/integration/ -v

# v0.3.0 acceptance tests (needs SG/Send dev branch installed)
git clone --depth 1 --branch dev \
  https://github.com/the-cyber-boardroom/SGraph-AI__App__Send.git /tmp/sgraph-send-dev
pip install /tmp/sgraph-send-dev
python -m pytest tests/qa/v030/ -v

# Browser tests only (needs Chromium)
python -m playwright install chromium
python -m pytest tests/qa/v030/test__upload__single_file.py -v
```

---

*SG/Send QA — Test Catalogue — Librarian Reference*
