# Reference: CI/CD Pipelines

**Maintained by:** Librarian
**Last updated:** 2026-03-23

---

## Pipeline Architecture

```
Push to dev ──→ ci-pipeline__dev.yml ──→ ci-pipeline.yml (reusable)
                                              │
Push to main ─→ ci-pipeline__main.yml ─→──────┘
                                              │
                                    ┌─────────┴──────────┐
                                    │                     │
                              ┌─────┴─────┐    ┌─────────┴───────┐
                              │ Unit Tests │    │ Browser Tests   │
                              └───────────┘    │ → Screenshots   │
                                               │ → Generate Docs │
                                               │ → Diff & Commit │
                                               └─────────────────┘
                                    │                     │
                              ┌─────┴──────┐    ┌────────┴────────┐
                              │ Increment  │    │ Deploy Docs     │
                              │ Tag        │    │ (Jekyll → Pages)│
                              └────────────┘    └─────────────────┘

Push to dev ──→ qa-acceptance-tests.yml
                     │
               ┌─────┴──────┐
               │ P0 Gate    │──→ fail = pipeline fails
               │ P1 Suite   │──→ fail = flag for review
               │ P2/P3 Suite│──→ informational
               │ QA Summary │──→ posts final status
               └────────────┘
```

---

## Workflow Files

### `.github/workflows/ci-pipeline.yml` — Reusable Base

The core workflow, called by branch-specific triggers via `workflow_call`.

| Job | Steps | Notes |
|-----|-------|-------|
| `run-unit-tests` | Install deps → `pytest tests/unit/ -v` | Fast, no browser |
| `run-browser-tests` | Install deps → Install Chromium → Run Playwright tests → Capture screenshots → Generate docs → Diff screenshots → Auto-commit | Full pipeline |
| `increment-tag` | Compute next semver → Update version files → Commit + tag + push | Conditional on success |
| `deploy-docs` | Jekyll build → GitHub Pages deploy | Uses `sg_send_qa__site/` |

### `.github/workflows/ci-pipeline__dev.yml` — Dev Trigger

- **Trigger:** push to `dev`
- **Calls:** `ci-pipeline.yml` with `release_type: minor` (bumps patch version)

### `.github/workflows/ci-pipeline__main.yml` — Main Trigger

- **Trigger:** push to `main`
- **Calls:** `ci-pipeline.yml` with `release_type: major` (bumps minor version, resets patch)

### `.github/workflows/qa-acceptance-tests.yml` — Acceptance Gates

- **Trigger:** push to `dev`
- **Jobs:** P0 gate → P1 suite → P2/P3 suite → QA summary
- **Purpose:** Priority-gated testing with different failure modes per level

### `.github/workflows/deploy-gh-pages.yml` — (Disabled)

Legacy standalone deployment. Functionality merged into `ci-pipeline.yml`.

---

## Custom Actions

### `.github/actions/git__increment-tag/action.yml`

Composite action for semver version management.

| Input | Values | Effect |
|-------|--------|--------|
| `release_type: minor` | Used by `dev` | Bumps patch number (e.g., v0.2.5 → v0.2.6) |
| `release_type: major` | Used by `main` | Bumps minor, resets patch (e.g., v0.2.6 → v0.3.0) |

**Files updated by this action:**
- `README.md` (version badge/text)
- `sg_send_qa/version`
- `pyproject.toml`

---

## Deployment

| Target | Method | URL |
|--------|--------|-----|
| GitHub Pages | Jekyll build in CI | [qa.send.sgraph.ai](https://qa.send.sgraph.ai) |

---

*SG/Send QA — CI/CD Reference — Librarian Reference*
