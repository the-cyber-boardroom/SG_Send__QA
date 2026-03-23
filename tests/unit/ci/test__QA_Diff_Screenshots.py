"""Unit tests for sg_send_qa.ci.QA_Diff_Screenshots."""
import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from sg_send_qa.ci.QA_Diff_Screenshots import QA_Diff_Screenshots


def _make_image(width=10, height=10, color=(255, 0, 0)):
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return img, buf.getvalue()


class TestQA_Diff_Screenshots_Defaults:
    def test_default_threshold(self):
        d = QA_Diff_Screenshots()
        assert d.threshold == 0.01

    def test_default_screenshots_dir(self):
        d = QA_Diff_Screenshots()
        assert d.screenshots_dir == "sg_send_qa__site/"


class TestQA_Diff_Screenshots_LoadThreshold:
    def test_returns_default_when_no_config(self, tmp_path):
        d = QA_Diff_Screenshots(config_path=str(tmp_path / "missing.json"))
        assert d.load_threshold() == 0.01

    def test_reads_threshold_from_config(self, tmp_path):
        cfg = {"screenshots": {"visual_diff_threshold": 0.05}}
        p   = tmp_path / "test-config.json"
        p.write_text(json.dumps(cfg))
        d = QA_Diff_Screenshots(config_path=str(p))
        assert d.load_threshold() == 0.05


class TestQA_Diff_Screenshots_PixelDiff:
    def test_identical_images_zero_diff(self):
        img, _ = _make_image(color=(255, 0, 0))
        d = QA_Diff_Screenshots()
        assert d.pixel_diff_ratio(img, img) == 0.0

    def test_different_sizes_returns_one(self):
        img_a, _ = _make_image(10, 10)
        img_b, _ = _make_image(20, 20)
        d = QA_Diff_Screenshots()
        assert d.pixel_diff_ratio(img_a, img_b) == 1.0

    def test_fully_different_images(self):
        img_a, _ = _make_image(color=(0,   0,   0))
        img_b, _ = _make_image(color=(255, 255, 255))
        d = QA_Diff_Screenshots()
        assert d.pixel_diff_ratio(img_a, img_b) == 1.0


class TestQA_Diff_Screenshots_Run:
    def test_no_changed_screenshots(self):
        d = QA_Diff_Screenshots()
        with patch.object(d, "load_threshold", return_value=0.01), \
             patch.object(d, "get_changed_screenshots", return_value=[]):
            result = d.run()
        assert result == {"threshold": 0.01, "checked": 0, "reverted": 0, "kept": 0}

    def test_new_file_is_kept(self, tmp_path):
        img, img_bytes = _make_image()
        png = tmp_path / "01_landing.png"
        img.save(str(png))

        d = QA_Diff_Screenshots()
        with patch.object(d, "load_threshold", return_value=0.01), \
             patch.object(d, "get_changed_screenshots", return_value=[str(png)]), \
             patch.object(d, "git_show_head", return_value=None):
            result = d.run()

        assert result["kept"] == 1
        assert result["reverted"] == 0

    def test_unchanged_image_is_reverted(self, tmp_path):
        img, img_bytes = _make_image()
        png = tmp_path / "01_landing.png"
        img.save(str(png))

        d = QA_Diff_Screenshots()
        with patch.object(d, "load_threshold", return_value=0.01), \
             patch.object(d, "get_changed_screenshots", return_value=[str(png)]), \
             patch.object(d, "git_show_head", return_value=img_bytes), \
             patch.object(d, "revert_file") as mock_revert:
            result = d.run()

        mock_revert.assert_called_once_with(str(png))
        assert result["reverted"] == 1
        assert result["kept"] == 0
