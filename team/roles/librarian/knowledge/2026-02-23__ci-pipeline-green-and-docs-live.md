# Knowledge Record: CI Pipeline Green & Documentation Live

**Date:** 2026-02-23
**Version:** v0.2.2
**Author:** Librarian

---

## Milestone 1: CI Pipeline Fully Green

All 4 jobs in the CI pipeline now pass on both `dev` and `main` branches.

### Jobs

| # | Job | Description |
|---|-----|-------------|
| 1 | **Run Unit Tests** | `pytest tests/unit/ -v` |
| 2 | **Run Browser Tests** | Playwright integration tests against `https://send.sgraph.ai`, captures screenshots, generates docs, auto-commits changes |
| 3 | **Increment Tag** | Semver tagging via custom composite action; `minor` release type on `dev` (bumps patch), `major` on `main` (bumps minor, resets patch) |
| 4 | **Deploy Documentation** | Jekyll build + GitHub Pages deployment |

### Pipeline Structure

- `ci-pipeline__dev.yml` -- triggers on push to `dev`, calls reusable workflow
- `ci-pipeline__main.yml` -- triggers on push to `main`, calls reusable workflow
- `ci-pipeline.yml` -- reusable base workflow containing all 4 jobs

### Fixes That Unblocked CI

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| **Increment Tag job failed** | `GIT__BRANCH` env var was not set; the composite action uses `${{ env.GIT__BRANCH }}` for checkout and push | Added `GIT__BRANCH` to the `env:` block of `ci-pipeline.yml`, populated from `${{ inputs.git_branch }}` |
| **Deploy Documentation job failed** | Ruby/Bundler could not find the `Gemfile`; `working-directory` was not set for the Ruby setup step | Added `working-directory: docs` to the `ruby/setup-ruby` step so Bundler finds the `Gemfile` in the correct directory |

---

## Milestone 2: Custom Domain Live

The GitHub Pages documentation site is now published at:

**https://qa.send.sgraph.ai/**

This is the living documentation site generated from screenshots captured during Playwright test runs. Content is built by Jekyll from the `sg_send_qa__site/` directory (and `docs/` in the deploy workflow).

---

## Cross-References

| Item | Path |
|------|------|
| Reusable CI pipeline | `.github/workflows/ci-pipeline.yml` |
| Dev trigger workflow | `.github/workflows/ci-pipeline__dev.yml` |
| Main trigger workflow | `.github/workflows/ci-pipeline__main.yml` |
| Standalone Pages deploy | `.github/workflows/deploy-gh-pages.yml` |
| Increment tag action | `.github/actions/git__increment-tag/action.yml` |
| Jekyll site source | `sg_send_qa__site/` |
| Jekyll config | `sg_send_qa__site/_config.yml` |
| Version file | `sg_send_qa/version` (currently `v0.2.2`) |

---

## State After These Milestones

- CI is green on both `dev` and `main`
- Every push runs: unit tests, browser tests, tag increment, docs deploy
- Documentation auto-published to https://qa.send.sgraph.ai/
- Current version: v0.2.2
- Phase 2 in progress: Playwright browser tests are capturing screenshots and generating documentation

---

*SG/Send QA -- Librarian Knowledge Record -- 2026-02-23*
