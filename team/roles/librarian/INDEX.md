# SG/Send QA — Master Index

**Maintained by:** Librarian
**Last updated:** 2026-03-23
**Version:** v0.2.5

---

## What is This Project?

**SG/Send QA** is a standalone test suite and living documentation generator for [SG/Send](https://send.sgraph.ai), an encrypted file sharing platform by SGraph AI.

It does three things:
1. **Tests SG/Send** — Playwright browser automation against the real UI (no mocks)
2. **Captures screenshots** — every test step produces annotated screenshots
3. **Publishes documentation** — screenshots become a Jekyll site at [qa.send.sgraph.ai](https://qa.send.sgraph.ai)

Every test run produces **two outputs**: a pass/fail result AND a documentation page with screenshots.

→ For the full project intro, see [About This Project](ABOUT.md)

---

## Quick Navigation

| What you're looking for | Where to go |
|------------------------|-------------|
| **Project overview & how it works** | [`team/roles/librarian/ABOUT.md`](ABOUT.md) |
| **All test files** | [`team/roles/librarian/REF__tests.md`](REF__tests.md) |
| **CI/CD pipelines** | [`team/roles/librarian/REF__ci.md`](REF__ci.md) |
| **Documentation site structure** | [`team/roles/librarian/REF__site.md`](REF__site.md) |
| **Team roles & decisions** | [`team/roles/librarian/REF__team.md`](REF__team.md) |
| **Agent guidance** | [`.claude/CLAUDE.md`](../../../.claude/CLAUDE.md) |
| **Published QA site** | [qa.send.sgraph.ai](https://qa.send.sgraph.ai) |

---

## Artifact Map

### Source Code — `sg_send_qa/`

The main Python package. Everything is importable via `from sg_send_qa.<module> import ...`.

| Module | Path | Purpose |
|--------|------|---------|
| `utils/Version.py` | `sg_send_qa/utils/Version.py` | Reads `sg_send_qa/version`, exports `version__sg_send__qa` |
| `server/main.py` | `sg_send_qa/server/main.py` | FastAPI test runner — health check, test triggers, results, site hosting |
| `cli/run_tests.py` | `sg_send_qa/cli/run_tests.py` | CLI entry point — run tests, generate docs |
| `cli/generate_docs.py` | `sg_send_qa/cli/generate_docs.py` | Walks use-case dirs, scaffolds markdown, regenerates index |
| `ci/diff_screenshots.py` | `sg_send_qa/ci/diff_screenshots.py` | Visual diff noise gate — reverts <1% pixel changes |

### Tests — `tests/`

Three test suites at different levels. See [REF__tests.md](REF__tests.md) for the complete catalogue.

| Suite | Path | Tests | What it covers |
|-------|------|:-----:|----------------|
| **Unit** | `tests/unit/` | 1 file | QA project's own code (Version.py) |
| **Integration** | `tests/integration/user/` | 1 file (3 tests) | Browser tests against production SG/Send |
| **v0.3.0 Acceptance** | `tests/qa/v030/` | 12 files | Full acceptance suite — API, crypto, browser, zero-knowledge |

### Documentation Site — `sg_send_qa__site/`

Jekyll-based site published to GitHub Pages. See [REF__site.md](REF__site.md) for page-by-page details.

| Page | Path | Purpose |
|------|------|---------|
| Home | `sg_send_qa__site/pages/index.md` | Project overview, pipeline diagram, use-case table |
| Use Cases Index | `sg_send_qa__site/pages/use-cases/index.md` | All documented workflows |
| Roadmap | `sg_send_qa__site/pages/roadmap.md` | Planned user stories (US-04 through US-15) |
| Landing Page Loads | `sg_send_qa__site/pages/use-cases/landing_page_loads/` | 1 screenshot |
| Access Gate Present | `sg_send_qa__site/pages/use-cases/landing_page_has_access_gate/` | 1 screenshot |
| Invalid Token Rejected | `sg_send_qa__site/pages/use-cases/invalid_token_rejected/` | 3 screenshots |

### CI/CD — `.github/`

See [REF__ci.md](REF__ci.md) for the full pipeline breakdown.

| Workflow | Path | Trigger |
|----------|------|---------|
| Base pipeline (reusable) | `.github/workflows/ci-pipeline.yml` | Called by branch workflows |
| Dev pipeline | `.github/workflows/ci-pipeline__dev.yml` | Push to `dev` |
| Main pipeline | `.github/workflows/ci-pipeline__main.yml` | Push to `main` |
| QA acceptance tests | `.github/workflows/qa-acceptance-tests.yml` | Push to `dev` |
| Increment tag action | `.github/actions/git__increment-tag/action.yml` | Called by pipelines |

### Team — `team/`

See [REF__team.md](REF__team.md) for the full team structure.

| Area | Path | Contents |
|------|------|----------|
| 6 Role definitions | `team/roles/*/ROLE.md` | QA Lead, Dev, Architect, DevOps, Librarian, Sherpa |
| Knowledge base | `team/roles/librarian/knowledge/` | Milestone records |
| Human briefs | `team/humans/dinis_cruz/briefs/` | Task briefs from project owner |
| Human debriefs | `team/humans/dinis_cruz/debriefs/` | Session debriefs and reviews |

### Configuration

| File | Path | Purpose |
|------|------|---------|
| Python project | `pyproject.toml` | Poetry config, v0.2.5, Python 3.12+ |
| Dependencies | `requirements.txt` | playwright, fastapi, uvicorn, pillow, pytest, httpx |
| Test config | `tests/config/test-config.json` | Target URLs, screenshot settings, viewport size |
| Environment template | `tests/config/.env.example` | TEST_TARGET, TEST_TARGET_URL, TEST_ACCESS_TOKEN, ADMIN_API_KEY |
| Jekyll config | `sg_send_qa__site/_config.yml` | Site title, URL, plugins, nav structure |
| Agent guidance | `.claude/CLAUDE.md` | Project-wide rules for AI agents |
| Explorer guidance | `.claude/explorer/CLAUDE.md` | Explorer team session rules |

---

## Key Links

| Resource | URL / Path |
|----------|-----------|
| Published QA site | [qa.send.sgraph.ai](https://qa.send.sgraph.ai) |
| SG/Send (what we test) | [send.sgraph.ai](https://send.sgraph.ai) |
| SG/Send source (read-only ref) | [github.com/the-cyber-boardroom/SGraph-AI__App__Send](https://github.com/the-cyber-boardroom/SGraph-AI__App__Send) |
| This repo | [github.com/the-cyber-boardroom/SG_Send__QA](https://github.com/the-cyber-boardroom/SG_Send__QA) |

---

## Known Bugs in SG/Send (found by our tests)

| Bug | Endpoint | Detail |
|-----|----------|--------|
| Wrong `upload_url` in create response | `POST /api/transfers/create` | Returns `/transfers/upload/{id}` (missing `/api/` prefix) — that URL 404s |
| Duplicate FastAPI Operation IDs | Routes__Vault__Pointer.py | Multiple route duplicates — FastAPI warns on every startup |

---

## Version History

| Version | Date | Milestone |
|---------|------|-----------|
| v0.1.0 | 2026-02-22 | Bootstrap — repo structure, FastAPI skeleton, CLI skeleton, Version.py |
| v0.2.2 | 2026-02-23 | CI pipeline green, custom domain live (qa.send.sgraph.ai) |
| v0.2.5 | 2026-03-22 | v0.3.0 acceptance tests, Playwright browser tests, QA site with use cases |

---

*SG/Send QA — Master Index — maintained by Librarian*
