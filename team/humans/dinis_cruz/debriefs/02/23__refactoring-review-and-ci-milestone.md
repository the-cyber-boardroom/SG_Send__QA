# Team Debrief: 23 Feb 2026

**Subject:** Major file-location refactoring (commit `3184673`) + CI pipeline milestone
**Version:** v0.2.2
**Prepared by:** Architect, DevOps, QA Lead, Developer, Librarian

---

## Part 1: Milestones Achieved

### CI Pipeline Fully Green

All 4 jobs now pass: Unit Tests, Browser Tests, Increment Tag, Deploy Documentation.

Two fixes unblocked this:

| Fix | Root Cause |
|-----|-----------|
| Added `GIT__BRANCH` env var to `ci-pipeline.yml` | The `git__increment-tag` action uses `${{ env.GIT__BRANCH }}` but it was never set |
| Added `working-directory: docs` to Jekyll build step | `bundle exec` was looking for `Gemfile` in repo root, not `docs/` |

### Custom Domain Live

Documentation site published at **https://qa.send.sgraph.ai/** (GitHub Pages with custom domain).

---

## Part 2: Refactoring Analysis (commit `3184673`)

### What Was Done

Pure file-move refactoring -- 20 files renamed, **zero code changes** (0 insertions, 0 deletions).

Three structural moves:

| Move | Before | After | Intent |
|------|--------|-------|--------|
| Package consolidation | `cli/`, `server/`, `ci/` at repo root | `sg_send_qa/cli/`, `sg_send_qa/server/`, `sg_send_qa/ci/` | Single installable Python package |
| Site content co-location | `docs/` + separate `screenshots/` | `sg_send_qa__site/pages/use-cases/{name}/` with co-located `screenshots/` | Content bundles: each use-case is self-contained |
| Config scoping | `config/` at repo root | `tests/config/` | Config is test-scoped, belongs with tests |

### Architect's Assessment

**The refactoring is architecturally sound.** Both moves are improvements:

- **Single-package consolidation** means `pyproject.toml` declares one package root, imports become `from sg_send_qa.cli import ...`, and packaging for Lambda/Docker is a single `pip install .`.
- **Content co-location** follows the "content bundle" pattern. Each use-case directory contains its markdown and its screenshots. This is trivially scriptable, scales cleanly, and matches what static-site generators expect.

The `sg_send_qa__site/` naming follows the OSBot/CB double-underscore convention. Slightly unusual for an internal directory but causes no technical issues.

### The Problem: Zero Code Updates

The commit moved files but updated **zero internal references**. Every hardcoded path in the codebase still points to the old locations.

---

## Part 3: Complete Breakage Inventory

The team identified **27 stale path references** across **8 files**, plus 1 missing `__init__.py`.

### P0 -- Currently Broken (will fail on next CI run)

| # | File | Line(s) | Issue |
|---|------|---------|-------|
| 1 | `ci-pipeline.yml` | 79 | `python cli/generate_docs.py` -- file not found |
| 2 | `ci-pipeline.yml` | 82 | `python ci/diff_screenshots.py` -- file not found |
| 3 | `ci-pipeline.yml` | 88 | `file_pattern: "screenshots/ docs/"` -- directories don't exist, auto-commit silently commits nothing |
| 4 | `ci-pipeline.yml` | 119 | `cp -r screenshots/ docs/screenshots/` -- source doesn't exist |
| 5 | `ci-pipeline.yml` | 126, 129 | `working-directory: docs` -- directory doesn't exist |
| 6 | `deploy-gh-pages.yml` | 8-9 | `paths: ['docs/**', 'screenshots/**']` -- trigger never fires |
| 7 | `deploy-gh-pages.yml` | 36 | `cp -r screenshots/ docs/screenshots/` -- same as #4 |
| 8 | `deploy-gh-pages.yml` | 42-43 | `working-directory: docs` -- directory doesn't exist |
| 9 | `deploy-gh-pages.yml` | 46 | `--source docs` -- directory doesn't exist |
| 10 | `sg_send_qa/cli/run_tests.py` | 30, 45 | `from cli.generate_docs import generate_docs` -- `ModuleNotFoundError` |
| 11 | `sg_send_qa/ci/__init__.py` | (missing) | Package not importable via `python -m sg_send_qa.ci.*` |

### P1 -- Wrong Output (runs but produces incorrect results)

| # | File | Line(s) | Issue |
|---|------|---------|-------|
| 12 | `tests/conftest.py` | 63 | Screenshot fixture writes to orphan `screenshots/` at repo root instead of `sg_send_qa__site/pages/use-cases/{name}/screenshots/` |
| 13 | `sg_send_qa/ci/diff_screenshots.py` | 21 | Reads `config/test-config.json` (moved to `tests/config/`) -- silently falls back to default |
| 14 | `sg_send_qa/ci/diff_screenshots.py` | 31 | `git diff -- screenshots/` returns empty list -- no diffing ever occurs |
| 15 | `sg_send_qa/cli/generate_docs.py` | 17-18, 40 | Reads from `screenshots/` and writes to `docs/` -- both gone |
| 16 | `sg_send_qa/server/main.py` | 9-10 | `parent.parent / "docs"` resolves to `sg_send_qa/docs` (doesn't exist) |

### P2 -- Config Drift

| # | File | Line(s) | Issue |
|---|------|---------|-------|
| 17 | `tests/config/test-config.json` | 13, 19 | `"directory": "screenshots"` and `"output_directory": "docs"` -- stale |

### P3 -- Cleanup

| # | Issue |
|---|-------|
| 18 | Stale `docs/screenshots/` empty directory at repo root |
| 19 | Stale `server/__pycache__/` from old location |
| 20 | Docstring in `run_tests.py` line 5 references `python cli/run_tests.py` |
| 21 | Site markdown files have extra path segment in image links (e.g., `screenshots/landing_page_loads/01_landing.png` should be `screenshots/01_landing.png`) |

---

## Part 4: Proposed Fixes

### CI Pipeline (`ci-pipeline.yml`)

```yaml
# Line 79: generate docs
python sg_send_qa/cli/generate_docs.py

# Line 82: diff screenshots
python sg_send_qa/ci/diff_screenshots.py

# Line 88: auto-commit file pattern
file_pattern: "sg_send_qa__site/"

# Line 119: remove entirely (screenshots are co-located, no copy needed)

# Lines 126, 129: Jekyll working directory
working-directory: sg_send_qa__site
```

### Deploy Pages (`deploy-gh-pages.yml`)

```yaml
# Lines 8-9: trigger paths
paths:
  - 'sg_send_qa__site/**'

# Line 36: remove screenshot copy step entirely

# Lines 42-43: Ruby working directory
working-directory: sg_send_qa__site

# Line 46: Jekyll build
working-directory: sg_send_qa__site
run: bundle exec jekyll build --destination ../_site
```

### Python Files

| File | Fix |
|------|-----|
| `sg_send_qa/ci/__init__.py` | Create (empty file) |
| `sg_send_qa/ci/diff_screenshots.py:21` | `Path("tests/config/test-config.json")` |
| `sg_send_qa/ci/diff_screenshots.py:31` | `"sg_send_qa__site/"` in git diff arg |
| `sg_send_qa/cli/run_tests.py:30,45` | `from sg_send_qa.cli.generate_docs import generate_docs` |
| `sg_send_qa/cli/generate_docs.py` | Rewrite to walk `sg_send_qa__site/pages/use-cases/` and write co-located markdown |
| `sg_send_qa/server/main.py:9-10` | Use `parent.parent.parent / "sg_send_qa__site"` for site root |
| `tests/conftest.py:63` | `Path("sg_send_qa__site/pages/use-cases") / test_name / "screenshots"` |

### Config & Docs

| File | Fix |
|------|-----|
| `tests/config/test-config.json:13` | `"directory": "sg_send_qa__site/pages/use-cases"` |
| `tests/config/test-config.json:19` | `"output_directory": "sg_send_qa__site/pages"` |
| `sg_send_qa__site/pages/use-cases/*/*.md` | Fix relative image paths (remove extra `{test_name}/` segment) |
| `.claude/CLAUDE.md` | Update repo structure diagram and screenshot conventions |

---

## Part 5: Recommended Next Steps

### Immediate (before next push to dev)

1. **Fix all P0 items** -- CI will fail without these
2. **Create `sg_send_qa/ci/__init__.py`** -- required for package imports
3. **Update `conftest.py` screenshot path** -- tests write to wrong location without this

### Short-term (this sprint)

4. **Rewrite `generate_docs.py`** for the co-located content bundle structure
5. **Fix `deploy-gh-pages.yml`** -- currently will never trigger on docs changes
6. **Update `.claude/CLAUDE.md`** repo structure -- agents are working against stale guidance
7. **Fix markdown image paths** in existing use-case docs
8. **Clean up** stale `docs/screenshots/` and `server/__pycache__/`

### Testing after fixes

9. Run unit tests locally
10. Run integration tests to verify screenshots land in `sg_send_qa__site/`
11. Run `generate_docs.py` and verify output structure
12. Trigger CI on a test branch to validate the full pipeline
13. Verify Jekyll build produces working pages with screenshots at https://qa.send.sgraph.ai/

### Future considerations

14. Add unit tests for path resolution in `conftest.py`, `diff_screenshots.py`, and `generate_docs.py` to prevent future path regressions
15. Consider reading paths from `test-config.json` rather than hardcoding, so future moves only require config changes

---

## Appendix: Files Cross-Reference

| File | Role(s) That Reviewed |
|------|-----------------------|
| `.github/workflows/ci-pipeline.yml` | Architect, DevOps, QA Lead, Developer |
| `.github/workflows/deploy-gh-pages.yml` | DevOps, QA Lead |
| `tests/conftest.py` | QA Lead, Developer |
| `sg_send_qa/ci/diff_screenshots.py` | DevOps, QA Lead, Developer |
| `sg_send_qa/cli/generate_docs.py` | QA Lead, Developer |
| `sg_send_qa/cli/run_tests.py` | Developer |
| `sg_send_qa/server/main.py` | QA Lead, Developer |
| `tests/config/test-config.json` | DevOps, QA Lead, Developer |

---

*SG/Send QA -- Team Debrief -- 23 Feb 2026 -- v0.2.2*
