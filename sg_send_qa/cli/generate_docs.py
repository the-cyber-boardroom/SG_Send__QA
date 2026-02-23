#!/usr/bin/env python3
"""Generate markdown documentation from test screenshots.

Walks the sg_send_qa__site/pages/use-cases/ directory.  For each use case
that has a screenshots/_metadata.json (written by the conftest fixture),
it scaffolds a new markdown page if one doesn't already exist.

Existing hand-crafted pages are never overwritten — only their screenshot
sections could be refreshed in a future enhancement.

The index page (pages/index.md) is always regenerated to list every
use case found.

Timestamps are handled by the jekyll-last-modified-at plugin at build
time (reads git-log per file), so the generated markdown is stable and
only produces a diff when actual content changes.
"""
import json
from pathlib import Path

SITE_DIR      = Path("sg_send_qa__site")
USE_CASES_DIR = SITE_DIR / "pages" / "use-cases"
INDEX_PATH    = SITE_DIR / "pages" / "index.md"

FRONT_MATTER = '---\ntitle: "Use Case: {title}"\npermalink: /pages/use-cases/{name}/\n---\n'


def _title_from_name(name):
    return name.replace("_", " ").title()


def _read_metadata(use_case_dir):
    """Read _metadata.json from the screenshots subdirectory, if present."""
    meta_path = use_case_dir / "screenshots" / "_metadata.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text())
    return None


def _scaffold_page(use_case_dir, name, metadata):
    """Generate a starter markdown page for a new use case."""
    title = _title_from_name(name)
    md    = FRONT_MATTER.format(title=title, name=name)
    md   += f"\n# {title}\n\n"

    if metadata and metadata.get("test_doc"):
        md += f"{metadata['test_doc'].strip()}\n\n"
    else:
        md += f"Automated browser test for the **{title.lower()}** workflow.\n\n"

    md += "---\n\n"

    # Add screenshots
    screenshots = []
    if metadata and metadata.get("screenshots"):
        screenshots = metadata["screenshots"]
    else:
        shot_dir = use_case_dir / "screenshots"
        if shot_dir.exists():
            screenshots = [
                {"name": p.stem, "description": ""}
                for p in sorted(shot_dir.glob("*.png"))
            ]

    if screenshots:
        md += "## Screenshots\n\n"
        for shot in screenshots:
            desc  = shot.get("description", "") or shot["name"].replace("_", " ").title()
            label = shot["name"].replace("_", " ").title()
            md += f"### {label}\n\n"
            if shot.get("description"):
                md += f"{shot['description']}\n\n"
            md += f"![{label}](screenshots/{shot['name']}.png)\n\n"

    return md


def generate_docs():
    USE_CASES_DIR.mkdir(parents=True, exist_ok=True)

    use_cases = []

    for uc_dir in sorted(USE_CASES_DIR.iterdir()):
        if not uc_dir.is_dir():
            continue

        name     = uc_dir.name
        title    = _title_from_name(name)
        metadata = _read_metadata(uc_dir)

        # Check for existing markdown
        md_path = uc_dir / f"{name}.md"
        if not md_path.exists():
            # Scaffold a new page
            content = _scaffold_page(uc_dir, name, metadata)
            md_path.write_text(content)
            print(f"  Scaffolded: {md_path}")
        else:
            print(f"  Exists:     {md_path}")

        # Count screenshots
        shot_dir  = uc_dir / "screenshots"
        shot_count = len(list(shot_dir.glob("*.png"))) if shot_dir.exists() else 0

        use_cases.append((name, title, shot_count))

    # Regenerate index
    _generate_index(use_cases)


def _generate_index(use_cases):
    """Regenerate the index page listing all use cases."""
    md  = '---\ntitle: SG/Send QA Documentation\npermalink: /\n---\n\n'
    md += "# SG/Send QA\n\n"
    md += "Living documentation and automated test results for "
    md += "[SG/Send](https://send.sgraph.ai) — the encrypted file sharing platform.\n\n"
    md += "---\n\n"
    md += "## Use Cases\n\n"

    if use_cases:
        md += "| Use Case | Screenshots |\n"
        md += "|----------|:-----------:|\n"
        for name, title, shot_count in use_cases:
            md += f"| [{title}](use-cases/{name}/{name}) | {shot_count} |\n"
    else:
        md += "*No test use cases found. Run tests first.*\n"

    md += "\n---\n\n"
    md += "*This site is automatically generated from Playwright browser tests.*\n"

    # Only overwrite if the index has minimal/generated content
    # (check for the hand-crafted architecture section)
    if INDEX_PATH.exists():
        existing = INDEX_PATH.read_text()
        if "## Architecture" in existing:
            print(f"  Skipped:    {INDEX_PATH} (hand-crafted content preserved)")
            return

    INDEX_PATH.write_text(md)
    print(f"  Generated:  {INDEX_PATH} ({len(use_cases)} use cases)")


if __name__ == "__main__":
    generate_docs()
