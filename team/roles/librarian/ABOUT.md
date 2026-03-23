# About SG/Send QA

**Version:** v0.2.5
**Last updated:** 2026-03-23

---

## What is SG/Send?

[SG/Send](https://send.sgraph.ai) is an **encrypted file sharing platform** built by SGraph AI. Users get a time-limited access token, upload files through a browser UI, and the files are encrypted client-side with **AES-256-GCM** before leaving the browser. The encryption key lives only in the URL fragment — the server never sees plaintext.

Key properties:
- **Zero-knowledge architecture** — the server stores only ciphertext
- **Access gate** — users must present a valid token before they can do anything
- **Client-side encryption** — AES-256-GCM with SGMETA envelope format
- **Time-limited sharing** — tokens and transfers expire

---

## What is SG/Send QA?

This repository is a **standalone QA project** that tests SG/Send from the outside. It never modifies SG/Send code — it observes it, tests it, screenshots it, and publishes documentation about what it finds.

### The Core Idea

Every test run produces **two outputs**:

```
Test Run
  ├── Pass/Fail result     → Did the feature work?
  └── Screenshot pages     → Living documentation of what happened
```

This means the test suite is also the documentation generator. When tests pass, you get up-to-date docs. When tests fail, you get evidence of what's broken.

### What It Produces

| Output | Where | Updated |
|--------|-------|---------|
| **Test results** | CI pipeline logs | Every push |
| **Screenshots** | `sg_send_qa__site/pages/use-cases/*/screenshots/` | Every test run |
| **Documentation pages** | [qa.send.sgraph.ai](https://qa.send.sgraph.ai) | Auto-deployed via GitHub Pages |
| **Bug evidence** | Screenshots of buggy behaviour + Change Requests | When bugs are found |

---

## How It Works

### 1. Test Execution

Tests run in three tiers:

```
┌─────────────────────────────────────────────────────┐
│  Unit Tests (tests/unit/)                            │
│  → Test the QA project's own code (Version.py, etc) │
│  → Fast, no browser, no network                      │
├─────────────────────────────────────────────────────┤
│  Integration Tests (tests/integration/)              │
│  → Playwright browser tests against production       │
│  → Real HTTP, real screenshots, headless Chromium    │
├─────────────────────────────────────────────────────┤
│  Acceptance Tests (tests/qa/v030/)                   │
│  → Full suite against local SG/Send server           │
│  → API smoke tests, crypto validation, browser tests │
│  → In-memory server, no S3, no external deps         │
└─────────────────────────────────────────────────────┘
```

### 2. The Test Infrastructure (v0.3.0 Acceptance)

The acceptance test suite spins up a **real SG/Send server** in-process:

```
pytest session starts
    │
    ├── send_server fixture
    │     └── Starts real FastAPI server (from sgraph-ai-app-send dev branch)
    │         In-memory storage, random port, random access token
    │
    ├── ui_server fixture
    │     └── Copies SG/Send UI v0.3.0 into a temp dir
    │         Injects build-info.js pointing at the test server
    │         Serves on localhost:10062 (must be 'localhost' for Web Crypto)
    │
    └── transfer_helper fixture
          └── Creates encrypted transfers via API (no browser needed)
              Matches the browser's AES-256-GCM + SGMETA envelope exactly
```

This means tests run against a **real server with real crypto** — no mocks anywhere.

### 3. Screenshot Capture & Documentation

```
Test step → Playwright captures screenshot (1280×720)
         → Saved to sg_send_qa__site/pages/use-cases/{test}/screenshots/
         → Visual diff compares against previous version
         → Changes >1% are kept (real UI change)
         → Changes ≤1% are reverted (rendering noise)
         → generate_docs.py scaffolds markdown page
         → Jekyll builds static site
         → GitHub Pages deploys to qa.send.sgraph.ai
```

### 4. CI Pipeline

Every push triggers:

| Job | What it does |
|-----|-------------|
| **Run Unit Tests** | `pytest tests/unit/ -v` |
| **Run Browser Tests** | Playwright tests → capture screenshots → generate docs → diff screenshots → auto-commit |
| **Increment Tag** | Semver bump via custom action (patch on `dev`, minor on `main`) |
| **Deploy Documentation** | Jekyll build → GitHub Pages |

The **QA Acceptance pipeline** adds priority gating:
- **P0** tests must pass (deployment blockers)
- **P1** tests flag for human review if failing
- **P2/P3** are informational

---

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Playwright over Selenium** | Native Python, pytest integration, auto-waiting, CDP screenshot support |
| **No mocks** | We test the real product. Mocks hide bugs. |
| **Jekyll for docs** | Simple, GitHub Pages native, markdown-first |
| **Content bundles** | Each use-case is a self-contained directory (markdown + screenshots together) |
| **Visual diff noise gate** | Sub-pixel rendering differences create noise commits; 1% threshold filters these |
| **In-memory test server** | Fast, isolated, no external dependencies — every test session is clean |
| **SGMETA envelope in tests** | TransferHelper matches the browser's exact encryption format — tests prove zero-knowledge |

---

## Project Structure

```
SG_Send__QA/
├── .claude/                    Agent guidance
│   ├── CLAUDE.md               Project-wide rules → points to role files
│   └── explorer/CLAUDE.md      Explorer team session rules
│
├── sg_send_qa/                 Python package
│   ├── version                 Current version (v0.2.5)
│   ├── utils/Version.py        Version reader
│   ├── server/main.py          FastAPI test runner API
│   ├── cli/run_tests.py        CLI test runner
│   ├── cli/generate_docs.py    Doc generator (walks use-cases, scaffolds markdown)
│   └── ci/diff_screenshots.py  Visual diff noise gate
│
├── tests/
│   ├── unit/                   Tests for QA project code
│   ├── integration/user/       Browser tests against production
│   └── qa/v030/                v0.3.0 acceptance suite (12 test files)
│       ├── conftest.py         Server fixtures, markers, browser setup
│       ├── test__access_gate.py
│       ├── test__upload__single_file.py
│       ├── test__zero_knowledge.py
│       └── ...
│
├── sg_send_qa__site/           Jekyll documentation site
│   ├── _config.yml             Site config (qa.send.sgraph.ai)
│   ├── _layouts/default.html   Layout with sidebar nav, Mermaid support
│   └── pages/
│       ├── index.md            Home page
│       ├── roadmap.md          Planned user stories (US-04 to US-15)
│       └── use-cases/          Documented test workflows
│           ├── index.md
│           ├── landing_page_loads/
│           ├── landing_page_has_access_gate/
│           └── invalid_token_rejected/
│
├── team/                       Team knowledge
│   ├── roles/                  6 role definitions (ROLE.md each)
│   │   ├── qa-lead/            Test strategy, quality gates, bug docs
│   │   ├── dev/                Implementation, Playwright rules, bug test pattern
│   │   ├── architect/          System design, tool decisions
│   │   ├── devops/             CI/CD, deployment
│   │   ├── librarian/          This index + knowledge records
│   │   └── sherpa/             Onboarding, best practices
│   └── humans/dinis_cruz/      Briefs and debriefs from project owner
│
└── .github/
    ├── workflows/              CI pipelines (dev, main, QA acceptance)
    └── actions/                Custom semver tag action
```

---

## Further Reading

| Topic | File |
|-------|------|
| Master index of all artifacts | [`team/roles/librarian/INDEX.md`](INDEX.md) |
| Test catalogue | [`team/roles/librarian/REF__tests.md`](REF__tests.md) |
| CI/CD reference | [`team/roles/librarian/REF__ci.md`](REF__ci.md) |
| Site structure | [`team/roles/librarian/REF__site.md`](REF__site.md) |
| Team & decisions | [`team/roles/librarian/REF__team.md`](REF__team.md) |
| Agent guidance | [`.claude/CLAUDE.md`](../../../.claude/CLAUDE.md) |
| QA Lead role | [`team/roles/qa-lead/ROLE.md`](../qa-lead/ROLE.md) |
| Developer role | [`team/roles/dev/ROLE.md`](../dev/ROLE.md) |
| Explorer team guide | [`.claude/explorer/CLAUDE.md`](../../../.claude/explorer/CLAUDE.md) |

---

*SG/Send QA — About This Project — v0.2.5*
