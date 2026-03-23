# Reference: Documentation Site

**Maintained by:** Librarian
**Last updated:** 2026-03-23

---

## Overview

The QA site is a **Jekyll static site** published to GitHub Pages at [qa.send.sgraph.ai](https://qa.send.sgraph.ai).

Every page is generated from or backed by Playwright test screenshots. The site is rebuilt and redeployed on every push to `dev` or `main`.

---

## Site Structure

```
sg_send_qa__site/
├── _config.yml                   Jekyll configuration
├── Gemfile                       Ruby dependencies (jekyll ~> 4.3)
├── _layouts/
│   └── default.html              Layout: sidebar nav, Mermaid diagrams, footer
└── pages/
    ├── index.md                  Home page — overview, pipeline diagram, use-case table
    ├── roadmap.md                Planned user stories (US-04 to US-15)
    └── use-cases/
        ├── index.md              Use cases overview — workflow diagram, table
        ├── landing_page_loads/
        │   ├── landing_page_loads.md
        │   └── screenshots/
        │       ├── 01_landing.png
        │       └── _metadata.json
        ├── landing_page_has_access_gate/
        │   ├── landing_page_has_access_gate.md
        │   └── screenshots/
        │       ├── 01_access_gate.png
        │       └── _metadata.json
        ├── invalid_token_rejected/
        │   ├── invalid_token_rejected.md
        │   └── screenshots/
        │       ├── 01_before_token.png
        │       ├── 02_token_entered.png
        │       ├── 03_token_rejected.png
        │       └── _metadata.json
        ├── bugs/
        │   └── screenshots/      (placeholder — bug documentation)
        └── route_handling/
            └── screenshots/      (placeholder — route tests)
```

---

## Page Inventory

| Page | Permalink | Content |
|------|-----------|---------|
| **Home** | `/` | What is SG/Send, what is this site, pipeline architecture, use-case table, visual diff explanation |
| **Use Cases Index** | `/pages/use-cases/` | Landing & authentication workflow diagram, table of all use cases with screenshot counts |
| **Roadmap** | `/pages/roadmap/` | 12 planned user stories (US-04 to US-15), priority summary, Gantt chart, story lifecycle |
| **Landing Page Loads** | `/pages/use-cases/landing_page_loads/` | Screenshot of initial page load, what it verifies |
| **Access Gate Present** | `/pages/use-cases/landing_page_has_access_gate/` | Screenshot of token input UI |
| **Invalid Token Rejected** | `/pages/use-cases/invalid_token_rejected/` | 3-step flow: before token, token entered, rejection error |

---

## Content Bundle Pattern

Each use case follows the same self-contained directory structure:

```
{use_case_name}/
├── {use_case_name}.md        Documentation page (Jekyll front matter + markdown)
└── screenshots/
    ├── 01_{step}.png         Screenshots captured during test
    ├── 02_{step}.png
    └── _metadata.json        Screenshot metadata (descriptions, test name, capture time)
```

**Key conventions:**
- Screenshots are 1280×720 PNG
- Naming: `{NN}_{description}.png` (e.g., `01_landing.png`)
- `_metadata.json` records what each screenshot shows
- The markdown page references screenshots via relative paths

---

## Screenshot Metadata (`_metadata.json`)

Each screenshots directory contains a metadata file:

```json
{
  "test_name": "test_landing_page_loads",
  "screenshots": [
    {
      "filename": "01_landing.png",
      "description": "SG/Send landing page with Beta Access gate"
    }
  ]
}
```

This is consumed by `generate_docs.py` when scaffolding new documentation pages.

---

## How New Pages Are Created

1. A new test in `tests/integration/` or `tests/qa/v030/` captures screenshots
2. Screenshots land in `sg_send_qa__site/pages/use-cases/{test_name}/screenshots/`
3. `generate_docs.py` detects the new directory and scaffolds a markdown page
4. The use-cases index is regenerated to include the new entry
5. CI commits, Jekyll builds, GitHub Pages deploys

---

## Site Configuration

### `_config.yml` highlights

- **title:** SG/Send QA
- **url:** https://qa.send.sgraph.ai
- **plugins:** jekyll-last-modified-at (shows last-modified timestamp in footer)
- **navigation:** Defined in config, rendered by `default.html` layout

### Layout features (`default.html`)

- Sidebar navigation with breadcrumbs
- Responsive grid
- Mermaid diagram support (loaded from CDN)
- Custom colour scheme
- Footer with last-modified-at timestamp

---

*SG/Send QA — Site Structure Reference — Librarian Reference*
