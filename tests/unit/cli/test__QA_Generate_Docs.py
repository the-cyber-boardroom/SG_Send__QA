"""Unit tests for sg_send_qa.cli.QA_Generate_Docs."""
import json
from pathlib import Path

import pytest

from sg_send_qa.cli.QA_Generate_Docs import QA_Generate_Docs


def _make_generator(tmp_path) -> QA_Generate_Docs:
    return QA_Generate_Docs(
        site_dir  = str(tmp_path / "site"),
        tests_dir = str(tmp_path / "tests"),
    )


class TestQA_Generate_Docs_Defaults:
    def test_default_site_dir(self):
        g = QA_Generate_Docs()
        assert g.site_dir == "sg_send_qa__site"

    def test_default_tests_dir(self):
        g = QA_Generate_Docs()
        assert g.tests_dir == "tests/qa/v030"


class TestQA_Generate_Docs_Helpers:
    def test_title_from_name(self):
        g = QA_Generate_Docs()
        assert g.title_from_name("access_gate") == "Access Gate"

    def test_read_metadata_missing(self, tmp_path):
        g = _make_generator(tmp_path)
        assert g.read_metadata(tmp_path / "nonexistent") is None

    def test_read_metadata_present(self, tmp_path):
        uc_dir = tmp_path / "my_use_case"
        shots  = uc_dir / "screenshots"
        shots.mkdir(parents=True)
        meta   = {"use_case": "my_use_case", "tests": []}
        (shots / "_metadata.json").write_text(json.dumps(meta))

        g = _make_generator(tmp_path)
        assert g.read_metadata(uc_dir) == meta

    def test_read_test_source_missing(self, tmp_path):
        g = _make_generator(tmp_path)
        assert g.read_test_source("nonexistent") is None

    def test_read_test_source_present(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        src = "def test_foo(): pass"
        (tests_dir / "test__my_uc.py").write_text(src)

        g = QA_Generate_Docs(site_dir=str(tmp_path / "site"),
                              tests_dir=str(tests_dir))
        assert g.read_test_source("my_uc") == src


class TestQA_Generate_Docs_Scaffold:
    def test_scaffold_page_contains_title(self, tmp_path):
        g    = _make_generator(tmp_path)
        uc   = tmp_path / "site" / "pages" / "use-cases" / "my_uc"
        md   = g.scaffold_page(uc, "my_uc", None)
        assert "My Uc" in md

    def test_scaffold_page_uses_module_doc(self, tmp_path):
        g    = _make_generator(tmp_path)
        uc   = tmp_path / "site" / "pages" / "use-cases" / "my_uc"
        meta = {"module_doc": "This is the module docstring.", "tests": [], "screenshots": []}
        md   = g.scaffold_page(uc, "my_uc", meta)
        assert "This is the module docstring." in md

    def test_scaffold_page_lists_tests(self, tmp_path):
        g    = _make_generator(tmp_path)
        uc   = tmp_path / "site" / "pages" / "use-cases" / "my_uc"
        meta = {
            "tests": [{"method": "test_foo", "doc": "Does foo.", "screenshots": ["01_foo"]}],
            "screenshots": [],
        }
        md   = g.scaffold_page(uc, "my_uc", meta)
        assert "foo" in md
        assert "Does foo." in md

    def test_scaffold_page_includes_screenshots(self, tmp_path):
        g    = _make_generator(tmp_path)
        uc   = tmp_path / "site" / "pages" / "use-cases" / "my_uc"
        meta = {
            "tests": [],
            "screenshots": [{"name": "01_landing", "description": "Landing page"}],
        }
        md   = g.scaffold_page(uc, "my_uc", meta)
        assert "01_landing.png" in md
        assert "Landing page" in md


class TestQA_Generate_Docs_Groups:
    def _make_group(self, tmp_path, group_id="01-access-gate",
                    uc_name="my_uc", manifest=None):
        g        = _make_generator(tmp_path)
        grp_dir  = g.use_cases_dir / group_id
        uc_dir   = grp_dir / uc_name
        uc_dir.mkdir(parents=True)
        if manifest:
            import json
            (grp_dir / "_group.json").write_text(json.dumps(manifest))
        return g, grp_dir, uc_dir

    def test_discover_groups_finds_numbered_dir(self, tmp_path):
        g, grp_dir, _ = self._make_group(tmp_path)
        groups = g.discover_groups()
        assert len(groups) == 1
        assert groups[0][0] == grp_dir

    def test_discover_groups_excludes_underscored(self, tmp_path):
        g = _make_generator(tmp_path)
        (g.use_cases_dir / "_archived").mkdir(parents=True)
        (g.use_cases_dir / "01-real").mkdir(parents=True)
        groups = g.discover_groups()
        assert len(groups) == 1

    def test_discover_members_excludes_underscored(self, tmp_path):
        g, grp_dir, uc_dir = self._make_group(tmp_path)
        (grp_dir / "_duplicates").mkdir(parents=True)
        members = g.discover_members(grp_dir)
        assert len(members) == 1
        assert members[0] == uc_dir

    def test_read_group_manifest(self, tmp_path):
        manifest = {"name": "Access Gate", "icon": "🔐", "description": "test", "duplicates": {}}
        g, grp_dir, _ = self._make_group(tmp_path, manifest=manifest)
        result = g.read_group_manifest(grp_dir)
        assert result["name"] == "Access Gate"

    def test_read_group_manifest_missing(self, tmp_path):
        g, grp_dir, _ = self._make_group(tmp_path)
        assert g.read_group_manifest(grp_dir) is None

    def test_generate_creates_use_cases_dir(self, tmp_path):
        g = _make_generator(tmp_path)
        g.generate()
        assert g.use_cases_dir.exists()

    def test_generate_scaffolds_new_page_in_group(self, tmp_path):
        g, grp_dir, uc_dir = self._make_group(tmp_path)
        g.generate()
        assert (uc_dir / "my_uc.md").exists()

    def test_generate_does_not_overwrite_existing_page(self, tmp_path):
        g, grp_dir, uc_dir = self._make_group(tmp_path)
        existing = "# Hand-crafted\n\n## Architecture\n"
        (uc_dir / "my_uc.md").write_text(existing)

        g.generate()

        assert (uc_dir / "my_uc.md").read_text() == existing

    def test_generate_returns_use_case_list(self, tmp_path):
        g, grp_dir, uc_dir = self._make_group(tmp_path)
        result = g.generate()
        assert isinstance(result, list)
        assert result[0][0] == "my_uc"

    def test_generate_includes_group_in_result(self, tmp_path):
        g, grp_dir, uc_dir = self._make_group(tmp_path, group_id="01-access-gate")
        result = g.generate()
        assert result[0][3] == "01-access-gate"
