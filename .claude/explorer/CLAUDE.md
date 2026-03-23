# SG/Send QA — Explorer Team Session

**You are operating as the Explorer team.** Read the root `.claude/CLAUDE.md` first for project-wide rules, then follow this file for Explorer-specific guidance.

---

## Current State (as of 2026-03-22)

**Branch:** `claude/create-qa-explorer-team-NUOoS`

### What exists and works

```
tests/qa/v030/
├── conftest.py                  ← session fixtures (API server + UI server + Playwright)
├── test__transfer_helper.py     ← 22 unit tests for client-side AES-256-GCM crypto helper
├── test__api_smoke.py           ← 21 API integration tests (create/upload/complete/download/info)
├── test__zero_knowledge.py      ← 5 zero-knowledge property tests (server never sees plaintext)
└── test__upload__single_file.py ← 4 Playwright browser tests (needs Chromium)
```

**48 tests passing** (transfer_helper + api_smoke + zero_knowledge).
Browser tests (`test__upload__single_file.py`) need Chromium — pass in CI, fail locally without network.

### How to run

```bash
# Install SG/Send from dev branch (required — do NOT use PyPI)
git clone --depth 1 --branch dev \
  https://github.com/the-cyber-boardroom/SGraph-AI__App__Send.git \
  /tmp/sgraph-send-dev
pip install /tmp/sgraph-send-dev

# Install QA deps
pip install -r requirements.txt

# Run non-browser tests (fast, no Chromium needed)
python -m pytest tests/qa/v030/test__transfer_helper.py \
                 tests/qa/v030/test__api_smoke.py \
                 tests/qa/v030/test__zero_knowledge.py -v

# Run all including browser tests (requires Chromium)
python -m playwright install chromium
python -m pytest tests/qa/v030/ -v
```

---

## Architecture — How the Test Stack Works

```
pytest session
    │
    ├── send_server fixture
    │     └── setup__send_user_lambda__test_server()
    │           Sets SGRAPH_SEND__ACCESS_TOKEN env var
    │           Starts real FastAPI (sgraph-ai-app-send dev branch)
    │           on a random port — in-memory storage, no S3, no network
    │
    ├── ui_server fixture  (only for Playwright tests)
    │     └── _build_ui_serve_dir()
    │           Copies sgraph_ai_app_send__ui__user/v0/v0.3/v0.3.0/
    │           into a tmp dir, injects build-info.js pointing at
    │           send_server.server_url, starts python -m http.server
    │           on localhost:10062
    │           IMPORTANT: must bind to 'localhost' not '127.0.0.1' —
    │           Web Crypto API requires a secure context
    │
    └── transfer_helper fixture
          └── TransferHelper — creates real encrypted transfers via
                the API without a browser:
                AES-256-GCM, 12-byte IV, SGMETA envelope, base64url key
```

**Key auth detail:** The API requires header `x-sgraph-access-token` (NOT `x-sgraph-send-access-token`). The token is `send_server.access_token` — a random GUID generated per session.

---

## Version Landscape

| Target | Version | Notes |
|--------|---------|-------|
| Production (send.sgraph.ai) | v0.13.0 (API) / UI v0.2.0 | Deployed 2026-03-08 |
| PyPI (sgraph-ai-app-send) | 0.16.0 | Do NOT use — behind dev |
| **dev branch (what we use)** | **0.16.50** | Always clone from GitHub |
| Local API (`/info/version`) | v1.34.0 | Internal versioning scheme |
| UI version under test | v0.3.0 | In `sgraph_ai_app_send__ui__user` |

The footer on the live UI shows: `v0.16.45 · UI v0.3.0`

---

## Bugs Found in SG/Send (dev branch)

| Bug | Endpoint | Detail |
|-----|----------|--------|
| Wrong `upload_url` in create response | `POST /api/transfers/create` | Returns `/transfers/upload/{id}` (missing `/api/` prefix) — that URL 404s. Correct path: `/api/transfers/upload/{id}` |
| Duplicate FastAPI Operation IDs | Routes__Vault__Pointer.py | `api_vault_write_put`, `api_vault_read_get`, `api_vault_read-base64_get`, `api_vault_delete_delete` all duplicated — FastAPI warns on every startup |

---

## Test Design Principles

- **No mocks** — real FastAPI server, real HTTP, real crypto
- **Every test is a QA assertion** — they find real bugs
- **TransferHelper** matches browser Web Crypto exactly — same SGMETA envelope, same AES-GCM params, same base64url key encoding
- **Screenshots** go in `sg_send_qa__site/pages/use-cases/{test_name}/screenshots/`
- **Priority markers:** `@pytest.mark.p0` (blocker), `p1` (sign-off), `p2` (filed), `p3` (nice-to-have)

---

## SGMETA Envelope Format

The browser encrypts files in this format before upload:

```
[SGMETA\0][4-byte big-endian meta_len][JSON metadata][plaintext content]
           └── encrypted with AES-256-GCM ──────────────────────────────┘
[12-byte random IV][ciphertext+auth_tag]   ← what the server stores
```

Key is 32 random bytes, base64url-encoded (no padding) in the URL fragment — never sent to the server.

---

## Current Priorities

| Priority | Task |
|----------|------|
| **P0** | Browser tests running in CI — Playwright + Chromium, ui_server fixture working |
| **P1** | Add test asserting footer shows `UI v0.3.0` — test written, needs Chromium to run |
| **P1** | File the `upload_url` bug against SG/Send dev |
| **P2** | Expand browser tests: access gate, multi-step upload flow, download flow |
| **P2** | Screenshot diff and documentation generation |
| **P3** | Admin panel tests |
