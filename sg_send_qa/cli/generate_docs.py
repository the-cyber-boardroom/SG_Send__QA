#!/usr/bin/env python3
"""Generate markdown documentation from test screenshots.

Each test directory under screenshots/ becomes a documentation page.
Screenshots are embedded with their descriptions.

Timestamps are handled by the jekyll-last-modified-at plugin at build
time (reads git-log per file), so the generated markdown is stable and
only produces a diff when actual content changes.
"""
from pathlib import Path

FRONT_MATTER = "---\n---\n"


def generate_docs():
    screenshots_dir = Path("screenshots")
    docs_dir        = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    index_entries = []

    for test_dir in sorted(screenshots_dir.iterdir()):
        if not test_dir.is_dir():
            continue

        test_name = test_dir.name
        shots     = sorted(test_dir.glob("*.png"))

        if not shots:
            continue

        title = test_name.replace("_", " ").title()
        md    = FRONT_MATTER
        md   += f"# {title}\n\n"
        md   += "*Last updated: {{ page.last_modified_at | date: '%Y-%m-%d %H:%M' }}*\n\n"

        for shot in shots:
            desc          = shot.stem.replace("_", " ").title()
            relative_path = f"screenshots/{test_name}/{shot.name}"
            md += f"## {desc}\n\n"
            md += f"![{desc}]({relative_path})\n\n"

        doc_path = docs_dir / f"{test_name}.md"
        doc_path.write_text(md)
        index_entries.append((test_name, title, f"{test_name}.md"))
        print(f"  Generated: {doc_path}")

    index_md  = FRONT_MATTER
    index_md += "# SG/Send QA Documentation\n\n"
    index_md += "Living documentation generated from automated browser tests.\n\n"
    index_md += "*Last updated: {{ page.last_modified_at | date: '%Y-%m-%d %H:%M' }}*\n\n"

    if index_entries:
        index_md += "## Test Pages\n\n"
        for name, title, path in index_entries:
            index_md += f"- [{title}]({path})\n"
    else:
        index_md += "*No test screenshots found. Run tests first.*\n"

    (docs_dir / "index.md").write_text(index_md)
    print(f"  Generated: docs/index.md ({len(index_entries)} pages)")


if __name__ == "__main__":
    generate_docs()
