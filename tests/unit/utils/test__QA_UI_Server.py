"""Unit tests for sg_send_qa.utils.QA_UI_Server."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from sg_send_qa.utils.QA_UI_Server import build_ui_serve_dir, UI_VERSION


class TestBuildUiServeDir:
    def test_ui_version_constant(self):
        assert UI_VERSION == "v0.3.0"

    def test_raises_if_ui_package_not_installed(self, tmp_path):
        """ImportError propagates when sgraph_ai_app_send__ui__user is absent."""
        with patch.dict("sys.modules", {"sgraph_ai_app_send__ui__user": None}):
            with pytest.raises((ImportError, TypeError)):
                build_ui_serve_dir("http://localhost:9999", tmp_path / "ui")

    def test_raises_if_ui_version_dir_missing(self, tmp_path):
        """RuntimeError raised when the version directory doesn't exist."""
        mock_pkg = MagicMock()
        mock_pkg.__file__ = str(tmp_path / "fake_pkg" / "__init__.py")

        with patch.dict("sys.modules", {"sgraph_ai_app_send__ui__user": mock_pkg}):
            with pytest.raises(RuntimeError, match="UI directory not found"):
                build_ui_serve_dir("http://localhost:9999", tmp_path / "serve")

    def test_creates_serve_dir(self, tmp_path):
        """serve_dir is created if it doesn't exist."""
        serve_dir = tmp_path / "ui-serve"
        ui_dir    = tmp_path / "fake_pkg" / "v0" / "v0.3" / "v0.3.0"

        # Minimal UI structure
        (ui_dir / "_common" / "js").mkdir(parents=True)
        (ui_dir / "_common" / "js" / "build-info.js").write_text("")
        (ui_dir / "en-gb").mkdir(parents=True)
        (ui_dir / "en-gb" / "index.html").write_text("<html></html>")

        mock_pkg = MagicMock()
        mock_pkg.__file__ = str(tmp_path / "fake_pkg" / "__init__.py")

        with patch.dict("sys.modules", {"sgraph_ai_app_send__ui__user": mock_pkg}):
            build_ui_serve_dir("http://localhost:9999", serve_dir)

        assert serve_dir.exists()

    def test_injects_api_endpoint_into_build_info(self, tmp_path):
        """build-info.js contains the injected API endpoint."""
        serve_dir = tmp_path / "ui-serve"
        ui_dir    = tmp_path / "fake_pkg" / "v0" / "v0.3" / "v0.3.0"

        (ui_dir / "_common" / "js").mkdir(parents=True)
        (ui_dir / "_common" / "js" / "build-info.js").write_text("")
        (ui_dir / "en-gb").mkdir(parents=True)
        (ui_dir / "en-gb" / "index.html").write_text("<html></html>")

        mock_pkg = MagicMock()
        mock_pkg.__file__ = str(tmp_path / "fake_pkg" / "__init__.py")

        with patch.dict("sys.modules", {"sgraph_ai_app_send__ui__user": mock_pkg}):
            build_ui_serve_dir("http://qa-server:54321", serve_dir,
                               comment="test run")

        build_info = (serve_dir / "_common" / "js" / "build-info.js").read_text()
        assert "http://qa-server:54321" in build_info
        assert "test run"               in build_info
