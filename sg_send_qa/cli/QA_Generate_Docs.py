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
from datetime import datetime, timezone
from pathlib import Path

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self as Type_Safe


FRONT_MATTER = '---\ntitle: "Use Case: {title}"\npermalink: /pages/use-cases/{group}/{name}/\n---\n'


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

    def scaffold_page(self, use_case_dir: Path, name: str, metadata: dict | None,
                      group_name: str = "") -> str:
        """Generate a starter markdown page for a new use case."""
        title = self.title_from_name(name)
        md    = FRONT_MATTER.format(title=title, group=group_name, name=name)
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
            shot_dir = use_case_dir / "screenshots"
            md += "## Screenshots\n\n"
            for shot in screenshots:
                name  = shot["name"]
                label = name.replace("_", " ").title()
                md += f"### {label}\n\n"
                if shot.get("description"):
                    md += f"{shot['description']}\n\n"
                md += f"![{label}](screenshots/{name}.png)\n\n"
                det_file = shot_dir / f"{name}__deterministic.png"
                if det_file.exists():
                    md += "<details>\n"
                    md += "<summary>Deterministic view (non-dynamic areas only)</summary>\n\n"
                    md += f"![{label} — masked](screenshots/{name}__deterministic.png)\n\n"
                    md += "</details>\n\n"

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

    def read_group_manifest(self, group_dir: Path) -> dict | None:
        """Read _group.json from a group directory, if present."""
        manifest_path = group_dir / "_group.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text())
        return None

    def discover_groups(self) -> list:
        """Walk use-cases dir and return list of (group_dir, manifest) for numbered dirs."""
        groups = []
        for d in sorted(self.use_cases_dir.iterdir()):
            if d.is_dir() and len(d.name) >= 2 and d.name[:2].isdigit():
                manifest = self.read_group_manifest(d)
                groups.append((d, manifest))
        return groups

    def discover_members(self, group_dir: Path) -> list:
        """Return list of use-case dirs inside a group (excludes _* dirs)."""
        members = []
        for d in sorted(group_dir.iterdir()):
            if d.is_dir() and not d.name.startswith("_"):
                members.append(d)
        return members

    def process_use_case(self, uc_dir: Path, group_name: str) -> tuple:
        """Scaffold page if missing, return (name, title, shot_count)."""
        name     = uc_dir.name
        title    = self.title_from_name(name)
        metadata = self.read_metadata(uc_dir)

        md_path = uc_dir / f"{name}.md"
        if not md_path.exists():
            content = self.scaffold_page(uc_dir, name, metadata, group_name=group_name)
            md_path.write_text(content)
            print(f"  Scaffolded: {md_path}")
        else:
            print(f"  Exists:     {md_path}")

        shot_dir   = uc_dir / "screenshots"
        shot_count = (len([p for p in shot_dir.glob("*.png")
                           if "__deterministic" not in p.name])
                      if shot_dir.exists() else 0)
        return (name, title, shot_count, group_name)

    def generate_grouped_index(self, groups_data: list) -> None:
        """Regenerate the index page with groups and use cases."""
        md  = '---\ntitle: SG/Send QA Documentation\npermalink: /\n---\n\n'
        md += "# SG/Send QA\n\n"
        md += "Living documentation and automated test results for "
        md += "[SG/Send](https://send.sgraph.ai) — the encrypted file sharing platform.\n\n"
        md += "---\n\n"

        for group_dir, manifest, members in groups_data:
            icon  = manifest.get("icon", "") if manifest else ""
            gname = manifest.get("name", group_dir.name) if manifest else group_dir.name
            desc  = manifest.get("description", "") if manifest else ""
            md += f"## {icon} {gname}\n\n"
            if desc:
                md += f"*{desc}*\n\n"
            if members:
                md += "| Use Case | Screenshots |\n"
                md += "|----------|:-----------:|\n"
                for name, title, shot_count, _ in members:
                    md += f"| [{title}](use-cases/{group_dir.name}/{name}/{name}) | {shot_count} |\n"
                md += "\n"

        md += "---\n\n"
        md += "*This site is automatically generated from Playwright browser tests.*\n"

        if self.index_path.exists():
            existing = self.index_path.read_text()
            if "## Architecture" in existing:
                print(f"  Skipped:    {self.index_path} (hand-crafted content preserved)")
                return

        self.index_path.write_text(md)
        total = sum(len(m) for _, _, m in groups_data)
        print(f"  Generated:  {self.index_path} ({len(groups_data)} groups, {total} use cases)")

    # kept for backward-compat (ungrouped callers)
    def generate_index(self, use_cases: list) -> None:
        """Regenerate the index page (flat list — legacy, prefer generate_grouped_index)."""
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
        """Walk grouped use-cases dir, scaffold missing pages, regenerate index.

        Returns flat list of (name, title, shot_count, group_name) tuples.
        """
        self.use_cases_dir.mkdir(parents=True, exist_ok=True)
        all_use_cases = []
        groups_data   = []

        for group_dir, manifest in self.discover_groups():
            members = []
            for uc_dir in self.discover_members(group_dir):
                entry = self.process_use_case(uc_dir, group_dir.name)
                members.append(entry)
                all_use_cases.append(entry)
            groups_data.append((group_dir, manifest, members))

        self.generate_grouped_index(groups_data)
        self.write_sidebar_data(groups_data)
        self.write_summary_data(groups_data)
        return all_use_cases

    # --------------------------------------------------------------- _data

    @property
    def data_dir(self) -> Path:
        return Path(self.site_dir) / "_data"

    def write_sidebar_data(self, groups_data: list) -> None:
        """Write _data/qa_sidebar.json for Jekyll sidebar rendering."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        groups = []
        for group_dir, manifest, members in groups_data:
            icon  = manifest.get("icon", "") if manifest else ""
            gname = manifest.get("name", group_dir.name) if manifest else group_dir.name
            items = []
            for name, title, shot_count, _ in members:
                items.append({
                    "id"       : name,
                    "title"    : title,
                    "group_id" : group_dir.name,
                    "composite": shot_count > 3,
                })
            groups.append({"id": group_dir.name, "name": gname, "icon": icon, "members": items})

        path = self.data_dir / "qa_sidebar.json"
        path.write_text(json.dumps({"groups": groups}, indent=2, ensure_ascii=False))
        print(f"  Written:    {path}")

    def write_summary_data(self, groups_data: list) -> None:
        """Write _data/qa_summary.json for Jekyll dashboard rendering."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        from sg_send_qa.utils.Version import version__sg_send__qa

        total_tests       = 0
        total_screenshots = 0
        zero_evidence     = 0
        group_summaries   = []
        needs_attention   = []

        for group_dir, manifest, members in groups_data:
            icon  = manifest.get("icon", "") if manifest else ""
            gname = manifest.get("name", group_dir.name) if manifest else group_dir.name
            g_total = len(members)
            g_with  = 0

            for name, title, shot_count, _ in members:
                total_screenshots += shot_count
                meta = self.read_metadata(group_dir / name)
                if meta:
                    total_tests += len(meta.get("tests", []))
                    if shot_count > 0:
                        g_with += 1
                    else:
                        zero_evidence += 1
                        needs_attention.append({"group": group_dir.name, "use_case": name})
                else:
                    zero_evidence += 1
                    needs_attention.append({"group": group_dir.name, "use_case": name})

            pct = round(g_with / g_total * 100) if g_total else 0
            group_summaries.append({
                "id"          : group_dir.name,
                "name"        : gname,
                "icon"        : icon,
                "total"       : g_total,
                "with_evidence": g_with,
                "coverage_pct": pct,
            })

        summary = {
            "generated_at"     : datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "version"          : version__sg_send__qa,
            "total_tests"      : total_tests,
            "total_screenshots": total_screenshots,
            "zero_evidence"    : zero_evidence,
            "groups"           : group_summaries,
            "needs_attention"  : needs_attention,
        }
        path = self.data_dir / "qa_summary.json"
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
        print(f"  Written:    {path}")
