"""Unit tests for sg_send_qa.utils.QA_Screenshot."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from sg_send_qa.utils.QA_Screenshot import cdp_screenshot


class TestCdpScreenshot:
    def test_creates_parent_dirs(self, tmp_path):
        """cdp_screenshot creates missing parent directories."""
        deep = tmp_path / "a" / "b" / "c" / "shot.png"

        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8   # minimal PNG header

        import base64
        mock_cdp = MagicMock()
        mock_cdp.send.return_value = {"data": base64.b64encode(fake_png).decode()}

        mock_page = MagicMock()
        mock_page.context.new_cdp_session.return_value = mock_cdp

        cdp_screenshot(mock_page, str(deep))

        assert deep.exists()
        assert deep.read_bytes() == fake_png

    def test_detaches_cdp_session(self, tmp_path):
        """cdp_screenshot always detaches the CDP session."""
        import base64
        mock_cdp = MagicMock()
        mock_cdp.send.return_value = {"data": base64.b64encode(b"PNG").decode()}

        mock_page = MagicMock()
        mock_page.context.new_cdp_session.return_value = mock_cdp

        cdp_screenshot(mock_page, str(tmp_path / "shot.png"))

        mock_cdp.detach.assert_called_once()

    def test_uses_png_format(self, tmp_path):
        """cdp_screenshot requests PNG format from CDP."""
        import base64
        mock_cdp = MagicMock()
        mock_cdp.send.return_value = {"data": base64.b64encode(b"PNG").decode()}

        mock_page = MagicMock()
        mock_page.context.new_cdp_session.return_value = mock_cdp

        cdp_screenshot(mock_page, str(tmp_path / "shot.png"))

        mock_cdp.send.assert_called_once_with(
            "Page.captureScreenshot", {"format": "png"}
        )
