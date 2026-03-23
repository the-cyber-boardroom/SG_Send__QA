"""Unit tests for sg_send_qa.utils.QA_Screenshot_Capture."""

import json
import base64
from pathlib import Path
from unittest.mock import MagicMock

from sg_send_qa.utils.QA_Screenshot_Capture import ScreenshotCapture


def _make_capture(tmp_path) -> ScreenshotCapture:
    return ScreenshotCapture(
        use_case    = "access_gate",
        module_name = "test__access_gate",
        module_doc  = "Test doc.",
        method_name = "test_upload_accessible_with_token",
        shots_dir   = tmp_path / "screenshots",
        test_target = "qa_server",
    )


def _fake_page(tmp_path):
    """Return a mock page that writes a tiny PNG via CDP."""
    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
    mock_cdp = MagicMock()
    mock_cdp.send.return_value = {"data": base64.b64encode(fake_png).decode()}
    mock_page = MagicMock()
    mock_page.context.new_cdp_session.return_value = mock_cdp
    return mock_page


class TestScreenshotCapture:
    def test_creates_shots_dir(self, tmp_path):
        cap = _make_capture(tmp_path)
        assert cap.shots_dir.exists()

    def test_capture_writes_png(self, tmp_path):
        cap  = _make_capture(tmp_path)
        page = _fake_page(tmp_path)
        cap.capture(page, "01_landing", "Landing page")
        assert (cap.shots_dir / "01_landing.png").exists()

    def test_all_returns_captured_list(self, tmp_path):
        cap  = _make_capture(tmp_path)
        page = _fake_page(tmp_path)
        assert cap.all == []
        cap.capture(page, "01_landing")
        assert len(cap.all) == 1
        assert cap.all[0]["name"] == "01_landing"

    def test_save_metadata_creates_json(self, tmp_path):
        cap  = _make_capture(tmp_path)
        page = _fake_page(tmp_path)
        cap.capture(page, "01_landing", "Landing")
        cap.save_metadata()

        meta = json.loads((cap.shots_dir / "_metadata.json").read_text())
        assert meta["use_case"]    == "access_gate"
        assert meta["test_target"] == "qa_server"
        assert len(meta["tests"])  == 1
        assert meta["tests"][0]["method"] == "test_upload_accessible_with_token"

    def test_save_metadata_deduplicates_on_rerun(self, tmp_path):
        """Re-running the same test method replaces the entry, not appends."""
        cap1 = _make_capture(tmp_path)
        page = _fake_page(tmp_path)
        cap1.capture(page, "01_landing")
        cap1.save_metadata()

        cap2 = _make_capture(tmp_path)   # same method_name
        cap2.capture(page, "01_landing")
        cap2.save_metadata()

        meta = json.loads((tmp_path / "screenshots" / "_metadata.json").read_text())
        # Only one entry for this method — not two
        methods = [t["method"] for t in meta["tests"]]
        assert methods.count("test_upload_accessible_with_token") == 1

    def test_save_metadata_accumulates_different_methods(self, tmp_path):
        """Two different test methods both appear in _metadata.json."""
        shots_dir = tmp_path / "screenshots"
        page      = _fake_page(tmp_path)

        cap1 = ScreenshotCapture("uc", "mod", "doc", "test_a", shots_dir)
        cap1.capture(page, "01_a")
        cap1.save_metadata()

        cap2 = ScreenshotCapture("uc", "mod", "doc", "test_b", shots_dir)
        cap2.capture(page, "02_b")
        cap2.save_metadata()

        meta    = json.loads((shots_dir / "_metadata.json").read_text())
        methods = [t["method"] for t in meta["tests"]]
        assert "test_a" in methods
        assert "test_b" in methods
