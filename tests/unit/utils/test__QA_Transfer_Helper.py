"""Unit tests for sg_send_qa.utils.QA_Transfer_Helper."""

from sg_send_qa.utils.QA_Transfer_Helper import QA_Transfer_Helper


class TestQA_Transfer_Helper:
    def test_defaults(self):
        h = QA_Transfer_Helper()
        assert h.api_url      == ""
        assert h.access_token == ""

    def test_headers_empty_without_token(self):
        h = QA_Transfer_Helper(api_url="http://localhost:9999")
        assert h._headers() == {}

    def test_headers_with_token(self):
        h = QA_Transfer_Helper(api_url="http://localhost:9999", access_token="tok-123")
        assert h._headers() == {"x-sgraph-access-token": "tok-123"}

    def test_sgmeta_magic_is_6_bytes(self):
        h = QA_Transfer_Helper()
        assert len(h.SGMETA_MAGIC) == 6
        assert h.SGMETA_MAGIC == bytes([0x53, 0x47, 0x4D, 0x45, 0x54, 0x41])

    def test_sgmeta_magic_spells_sgmeta(self):
        h = QA_Transfer_Helper()
        assert h.SGMETA_MAGIC.decode("ascii") == "SGMETA"

    def test_helpers_not_shared(self):
        """Each instance has independent state (no shared mutable defaults)."""
        a = QA_Transfer_Helper(api_url="http://a")
        b = QA_Transfer_Helper(api_url="http://b")
        assert a.api_url != b.api_url
