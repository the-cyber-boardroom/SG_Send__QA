---
title: "How the QA Site Works"
permalink: /pages/pipeline/
---

# How the QA Site Works

This page documents how [qa.send.sgraph.ai](https://qa.send.sgraph.ai) is built, updated, and deployed. The site is **living documentation** — every page is backed by automated Playwright browser tests that capture screenshots as evidence.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    GitHub Actions CI                      │
│                                                          │
│  1. Run unit tests (tests/unit/)                         │
│  2. Run browser tests (tests/integration/, tests/qa/)    │
│     └─ Playwright captures screenshots + metadata        │
│  3. generate_docs.py scaffolds new markdown pages        │
│  4. diff_screenshots.py reverts unchanged images         │
│  5. git-auto-commit-action commits sg_send_qa__site/     │
│  6. Jekyll builds the site                               │
│  7. deploy-pages publishes to GitHub Pages               │
│                                                          │
└──────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
  ┌──────────────┐                   ┌─────────────────┐
  │ Test Results  │                   │ qa.send.sgraph  │
  │ (pass/fail)   │                   │ .ai (live site) │
  └──────────────┘                   └─────────────────┘
```

## Step-by-Step Pipeline

### 1. Tests Run and Capture Screenshots

Each test uses the `screenshots` fixture from `tests/qa/v030/conftest.py`. When a test calls `screenshots.capture(page, name, description)`:

- A PNG is captured via Chrome DevTools Protocol (CDP)
- Saved to `sg_send_qa__site/pages/use-cases/{test_name}/screenshots/{name}.png`
- A `_metadata.json` file is written alongside with test docs and screenshot descriptions

```python
# In a test:
screenshots.capture(page, "01_landing", "Landing page with access gate")
```

This produces:
```
sg_send_qa__site/pages/use-cases/upload_accessible_with_token/
  screenshots/
    01_landing.png
    02_after_token.png
    _metadata.json
```

### 2. Documentation is Generated

`sg_send_qa/cli/generate_docs.py` walks the use-cases directory. For each folder with a `_metadata.json` but no markdown page, it scaffolds a starter page with:

- Front matter (title, permalink)
- Test docstring as description
- Screenshot gallery with descriptions

Hand-crafted pages (like the ones in this repo) are **never overwritten** — only new use cases get auto-scaffolded.

### 3. Screenshot Diffing

`sg_send_qa/ci/diff_screenshots.py` compares new screenshots against `git HEAD` using Pillow:

- If pixel difference < 1% → revert the file (no noisy commit)
- If pixel difference >= 1% → keep the new screenshot

This prevents meaningless commits from sub-pixel rendering differences across CI runs.

### 4. Auto-Commit

The `stefanzweifel/git-auto-commit-action` commits any changed files in `sg_send_qa__site/` with the message `"Update QA screenshots and docs [skip ci]"`.

### 5. Jekyll Build & Deploy

The `deploy-docs` job:

1. Sets up Ruby 3.3 + Bundler
2. Runs `bundle exec jekyll build` from `sg_send_qa__site/`
3. Uploads the built `_site/` as a Pages artifact
4. Deploys to GitHub Pages at `qa.send.sgraph.ai`

The `jekyll-last-modified-at` plugin reads git history to automatically show when each page was last updated.

---

## Adding a New Use Case

To add a new test that appears on the QA site:

### Option A: Auto-scaffolded (from test output)

1. Write a test in `tests/qa/v030/` that uses the `screenshots` fixture
2. The fixture creates the folder structure automatically
3. `generate_docs.py` creates a starter markdown page
4. CI commits and deploys

### Option B: Hand-crafted (richer documentation)

1. Create `sg_send_qa__site/pages/use-cases/{name}/` directory
2. Create `sg_send_qa__site/pages/use-cases/{name}/{name}.md` with Jekyll front matter
3. Create `sg_send_qa__site/pages/use-cases/{name}/screenshots/` directory
4. Write your test to capture screenshots into that directory
5. Add the use case to `_config.yml` navigation and the index page

### Naming Convention

The screenshot fixture derives the folder name from `request.node.name`:

```
test_upload_accessible_with_token → upload_accessible_with_token/
test_gallery_route                → gallery_route/
```

For class-based tests, only the method name is used (not the class name).

---

## Key Files

| File | Role |
|------|------|
| `tests/qa/v030/conftest.py` | Screenshot fixture, test server setup |
| `sg_send_qa/cli/generate_docs.py` | Auto-scaffolds markdown from metadata |
| `sg_send_qa/ci/diff_screenshots.py` | Visual diff, reverts unchanged PNGs |
| `sg_send_qa__site/_config.yml` | Jekyll config, navigation, custom domain |
| `.github/workflows/ci-pipeline.yml` | Full CI: test → screenshot → docs → deploy |

---

## Local Development

To preview the site locally:

```bash
cd sg_send_qa__site
bundle install
bundle exec jekyll serve
# → http://localhost:4000
```

To run v030 tests and capture screenshots locally:

```bash
python -m pytest tests/qa/v030/test__access_gate.py -v
python -m pytest tests/qa/v030/test__navigation.py -v
python -m sg_send_qa.cli.generate_docs
```

Screenshots will appear in `sg_send_qa__site/pages/use-cases/` ready for the site.
