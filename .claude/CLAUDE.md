# SG/Send QA — Agent Guidance

**Read this before starting any task.** This file is the single source of truth for all agents working on the SG/Send QA project.

---

## MEMORY.md Policy

**Do NOT use MEMORY.md** (the auto-memory at `~/.claude/projects/.../memory/MEMORY.md`). All persistent project knowledge is maintained in the repo itself.

---

## Project

**SG/Send QA** — browser automation test suite and living documentation generator for [send.sgraph.ai](https://send.sgraph.ai).

This is a **standalone project** (separate repo) that tests the SG/Send encrypted file sharing platform via headless browser automation and generates documentation from screenshots captured during test runs.

**You test SG/Send. You do not modify SG/Send.**

**Version file:** `sg_send_qa/version`

---

## Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Runtime | Python 3.12 | Same as SG/Send |
| Browser automation | Playwright for Python | Primary tool — native Python, pytest integration |
| Web framework | FastAPI | Test runner API |
| Documentation | Markdown + GitHub Pages | Generated from test screenshots |
| Testing | pytest + Playwright | Browser tests, no mocks |
| CI/CD | GitHub Actions | Test → screenshot → docs → deploy |
| Screenshot diff | Pillow | Visual regression detection |

---

## Architecture

- **One FastAPI server** — test runner API + documentation browser
- **CLI** — same capabilities as API, for terminal use
- **GitHub Actions** — CI pipeline: run tests → capture screenshots → generate docs → deploy to Pages
- **GitHub Pages** — published documentation site
- **Future: Lambda** — containerised test runner triggered by SG/Send deployments

```
Test Trigger (CI / API / CLI)
    │
    ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Playwright   │────▶│ Screenshot   │────▶│ Doc Generator   │
│ Test Runner  │     │ Library      │     │ (Markdown)      │
└─────────────┘     └──────────────┘     └─────────────────┘
    │                                          │
    ▼                                          ▼
┌─────────────┐                         ┌─────────────────┐
│ Test Results │                         │ GitHub Pages    │
│ (pass/fail)  │                         │ (published docs)│
└─────────────┘                         └─────────────────┘
```

---

## Repo Structure

```
SG_Send__QA/
├── .claude/
│   ├── CLAUDE.md               ← This file — agent guidance
│   └── explorer/CLAUDE.md      ← Explorer team session instructions
├── .github/workflows/
│   └── run-tests.yml           ← CI pipeline
├── config/
│   ├── test-config.json        ← Target URLs, test parameters
│   └── .env.example            ← Environment variable template
├── sg_send_qa/                 ← Python package
│   ├── utils/
│   │   └── Version.py
│   └── version                 ← Version file (v0.1.0)
├── tests/
│   ├── unit/                   ← Tests for sg_send_qa code
│   │   └── utils/test_Version.py
│   └── integration/            ← Browser automation tests
│       ├── user/               ← User Lambda tests
│       └── admin/              ← Admin Lambda tests
├── docs/                       ← Generated markdown + screenshots
│   └── index.md
├── screenshots/                ← Captured during test runs
├── server/
│   └── main.py                 ← FastAPI test runner
├── cli/
│   ├── run_tests.py            ← CLI test runner
│   └── generate_docs.py        ← Documentation generator
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Test Targets

| Target | URL | When |
|--------|-----|------|
| User Lambda (production) | `https://send.sgraph.ai` | Default smoke tests |
| Admin Panel (production) | `https://send.sgraph.ai/admin/` | Admin tests |
| User Lambda (local) | `http://localhost:10062` | Local development |
| Admin Lambda (local) | `http://localhost:10061` | Local development |

---

## Screenshot Conventions

- **Format:** PNG, 1280×720 viewport
- **Directory:** `screenshots/{test_name}/{step_name}.png`
- **Naming:** `{NN}_{description}.png` (e.g., `01_landing.png`, `02_token_entered.png`)
- **Visual diff threshold:** 1% pixel difference (ignore rendering noise)
- **Only commit changed screenshots** — visual diff before committing

---

## Key Rules

### Code Patterns

1. **Version prefix** on all review/doc files: `{version}__{description}.md`
2. **pytest** for all tests — no mocks, no patches
3. **Playwright** for browser automation — sync API, headless Chromium
4. **FastAPI** for the test runner server

### Testing

5. **No mocks, no patches** — real browser, real HTTP, real screenshots
6. **Every test captures screenshots** — tests produce pass/fail AND documentation
7. **Integration tests** live in `tests/integration/` (browser tests against running SG/Send)
8. **Unit tests** live in `tests/unit/` (tests for the QA project's own code)

### Git

9. **Default branch:** `main`
10. **Feature branches** branch from `main`
11. **Branch naming:** `claude/{description}-{session-id}`
12. **Always push with:** `git push -u origin {branch-name}`

---

## Roles (6 roles)

| Role | Responsibility |
|------|---------------|
| **QA Lead** | Drives priorities, defines test strategy, reviews test coverage |
| **Architect** | System design, tool decisions, API contracts |
| **Developer** | Implementation, test writing, doc generation |
| **DevOps** | CI/CD, GitHub Actions, deployment, Lambda |
| **Librarian** | Knowledge management, indexing, cross-references |
| **Sherpa** | Onboarding guidance, best practices, troubleshooting |

---

## Relationship to SG/Send

- **SG/Send main repo:** `https://github.com/the-cyber-boardroom/SGraph-AI__App__Send`
- **Clone read-only** for reference: `git clone --depth 1 <url> /tmp/sgraph-send-ref`
- This project **tests** SG/Send. It **never modifies** SG/Send code.
- Reference the main repo for: UI selectors, API routes, auth flow, component structure

---

## Current State (v0.1.0)

**Phase 1 complete.** Repo structure, FastAPI skeleton, CLI skeleton, GitHub Actions workflow, Version.py.

**Phase 2 in progress.** Playwright installed, first browser test capturing screenshots.

---
