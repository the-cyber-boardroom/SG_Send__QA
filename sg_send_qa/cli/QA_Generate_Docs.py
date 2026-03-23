"""Type_Safe class for generating markdown documentation from test screenshots.

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

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self as Type_Safe


FRONT_MATTER = '---\ntitle: "Use Case: {title}"\npermalink: /pages/use-cases/{name}/\n---\n'


class QA_Generate_Docs(Type_Safe):
    site_dir      : str = "sg_send_qa__site"
    tests_dir     : str = "tests/qa/v030"

    # -------------------------------------------------------------- properties

    @property
    def use_cases_dir(self) -> Path:
        return Path(self.site_dir) / "pages" / "use-cases"

    @property
    def index_path(self) -> Path:
        return Path(self.site_dir) / "pages" / "index.md"

    @property
    def tests_path(self) -> Path:
        return Path(self.tests_dir)

    # ---------------------------------------------------------------- helpers

    def title_from_name(self, name: str) -> str:
        return name.replace("_", " ").title()

    def read_metadata(self, use_case_dir: Path) -> dict | None:
        """Read _metadata.json from the screenshots subdirectory, if present."""
        meta_path = use_case_dir / "screenshots" / "_metadata.json"
        if meta_path.exists():
            return json.loads(meta_path.read_text())
        return None

    def read_test_source(self, use_case_name: str) -> str | None:
        """Read the test source file for a use case, if it exists."""
        test_path = self.tests_path / f"test__{use_case_name}.py"
        if test_path.exists():
            return test_path.read_text()
        return None

    # --------------------------------------------------------------- scaffold

    def scaffold_page(self, use_case_dir: Path, name: str, metadata: dict | None) -> str:
        """Generate a starter markdown page for a new use case."""
        title = self.title_from_name(name)
        md    = FRONT_MATTER.format(title=title, name=name)
        md   += f"\n# {title}\n\n"

        if metadata and metadata.get("module_doc"):
            md += f"{metadata['module_doc'].strip()}\n\n"
        elif metadata and metadata.get("test_doc"):
            md += f"{metadata['test_doc'].strip()}\n\n"
        else:
            md += f"Automated browser test for the **{title.lower()}** workflow.\n\n"

        md += "---\n\n"

        tests = metadata.get("tests", []) if metadata else []
        if tests:
            md += "## Test Methods\n\n"
            md += "| Method | Description | Screenshots |\n"
            md += "|--------|-------------|:-----------:|\n"
            for t in tests:
                method = t["method"].replace("test_", "")
                doc    = t.get("doc", "").split("\n")[0]
                count  = len(t.get("screenshots", []))
                md += f"| `{method}` | {doc} | {count} |\n"
            md += "\n"

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

        source = self.read_test_source(name)
        if source:
            md += "---\n\n"
            md += "## Test Source\n\n"
            md += f"**File:** `tests/qa/v030/test__{name}.py`\n\n"
            md += "```python\n"
            md += source
            md += "```\n\n"

        return md

    # --------------------------------------------------------------- generate

    def generate_index(self, use_cases: list) -> None:
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

        if self.index_path.exists():
            existing = self.index_path.read_text()
            if "## Architecture" in existing:
                print(f"  Skipped:    {self.index_path} (hand-crafted content preserved)")
                return

        self.index_path.write_text(md)
        print(f"  Generated:  {self.index_path} ({len(use_cases)} use cases)")

    def generate(self) -> list:
        """Walk use-cases dir, scaffold missing pages, regenerate index.

        Returns list of (name, title, shot_count) tuples for all use cases found.
        """
        self.use_cases_dir.mkdir(parents=True, exist_ok=True)
        use_cases = []

        for uc_dir in sorted(self.use_cases_dir.iterdir()):
            if not uc_dir.is_dir():
                continue

            name     = uc_dir.name
            title    = self.title_from_name(name)
            metadata = self.read_metadata(uc_dir)

            md_path = uc_dir / f"{name}.md"
            if not md_path.exists():
                content = self.scaffold_page(uc_dir, name, metadata)
                md_path.write_text(content)
                print(f"  Scaffolded: {md_path}")
            else:
                print(f"  Exists:     {md_path}")

            shot_dir   = uc_dir / "screenshots"
            shot_count = len(list(shot_dir.glob("*.png"))) if shot_dir.exists() else 0
            use_cases.append((name, title, shot_count))

        self.generate_index(use_cases)
        return use_cases
