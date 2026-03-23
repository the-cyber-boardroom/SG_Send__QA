"""Unit tests for sg_send_qa.models.QA_Config."""

from sg_send_qa.models.QA_Config import QA_Config


class TestQA_Config:
    def test_defaults_without_loading(self):
        cfg = QA_Config()
        assert cfg.screenshots.viewport_width        == 1280
        assert cfg.screenshots.viewport_height       == 720
        assert cfg.screenshots.visual_diff_threshold == 0.01
        assert cfg.docs.template                     == "default"

    def test_load_from_test_config(self):
        cfg = QA_Config().load()     # uses default path
        assert cfg.targets.production.user_url == "https://send.sgraph.ai"
        assert cfg.targets.local.user_url      == "http://localhost:10062"
        assert cfg.screenshots.viewport_width  == 1280

    def test_load_missing_file_returns_defaults(self):
        cfg = QA_Config().load("/tmp/nonexistent_qa_config_12345.json")
        assert cfg.screenshots.viewport_width == 1280   # defaults intact

    def test_targets_not_shared(self):
        a = QA_Config()
        b = QA_Config()
        a.targets.local.user_url = "http://changed"
        assert b.targets.local.user_url != "http://changed"
