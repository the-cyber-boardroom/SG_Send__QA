"""Unit tests for sg_send_qa.cli.QA_Run_Tests."""
import os
from unittest.mock import MagicMock, patch

import pytest

from sg_send_qa.cli.QA_Run_Tests import QA_Run_Tests


class TestQA_Run_Tests_Defaults:
    def test_default_target(self):
        r = QA_Run_Tests()
        assert r.target == "https://send.sgraph.ai"

    def test_default_flags(self):
        r = QA_Run_Tests()
        assert r.generate_docs is False
        assert r.docs_only     is False
        assert r.test          == ""


class TestQA_Run_Tests_FromArgs:
    def _args(self, target="https://example.com", test=None,
               generate_docs=False, docs_only=False):
        args = MagicMock()
        args.target        = target
        args.test          = test
        args.generate_docs = generate_docs
        args.docs_only     = docs_only
        return args

    def test_from_args_sets_target(self):
        r = QA_Run_Tests.from_args(self._args(target="http://localhost:9999"))
        assert r.target == "http://localhost:9999"

    def test_from_args_test_none_becomes_empty_string(self):
        r = QA_Run_Tests.from_args(self._args(test=None))
        assert r.test == ""

    def test_from_args_docs_only(self):
        r = QA_Run_Tests.from_args(self._args(docs_only=True))
        assert r.docs_only is True


class TestQA_Run_Tests_Run:
    def test_docs_only_calls_generate_docs(self):
        r = QA_Run_Tests(docs_only=True)
        with patch.object(r, "_run_generate_docs") as mock_gen:
            result = r.run()
        mock_gen.assert_called_once()
        assert result == 0

    def test_run_sets_env_var(self):
        r = QA_Run_Tests(target="http://qa-server:12345")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            r.run()
        assert os.environ.get("TEST_TARGET_URL") == "http://qa-server:12345"

    def test_run_returns_pytest_exit_code(self):
        r = QA_Run_Tests()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=42)
            result = r.run()
        assert result == 42

    def test_run_with_generate_docs_calls_generate(self):
        r = QA_Run_Tests(generate_docs=True)
        with patch("subprocess.run") as mock_run, \
             patch.object(r, "_run_generate_docs") as mock_gen:
            mock_run.return_value = MagicMock(returncode=0)
            r.run()
        mock_gen.assert_called_once()

    def test_run_with_test_filter_passes_k_flag(self):
        r = QA_Run_Tests(test="test_landing")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            r.run()
        cmd = mock_run.call_args[0][0]
        assert "-k" in cmd
        assert "test_landing" in cmd
