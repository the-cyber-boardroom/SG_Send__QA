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


class TestQA_Generate_Docs_Generate:
    def test_generate_creates_use_cases_dir(self, tmp_path):
        g = _make_generator(tmp_path)
        g.generate()
        assert g.use_cases_dir.exists()

    def test_generate_scaffolds_new_page(self, tmp_path):
        g      = _make_generator(tmp_path)
        uc_dir = g.use_cases_dir / "my_uc"
        uc_dir.mkdir(parents=True)

        g.generate()

        assert (uc_dir / "my_uc.md").exists()

    def test_generate_does_not_overwrite_existing_page(self, tmp_path):
        g      = _make_generator(tmp_path)
        uc_dir = g.use_cases_dir / "my_uc"
        uc_dir.mkdir(parents=True)
        existing = "# Hand-crafted\n\n## Architecture\n"
        (uc_dir / "my_uc.md").write_text(existing)

        g.generate()

        assert (uc_dir / "my_uc.md").read_text() == existing

    def test_generate_returns_use_case_list(self, tmp_path):
        g      = _make_generator(tmp_path)
        uc_dir = g.use_cases_dir / "my_uc"
        uc_dir.mkdir(parents=True)

        result = g.generate()

        assert isinstance(result, list)
        assert result[0][0] == "my_uc"
