"""Type_Safe wrapper for tests/config/test-config.json.

Loads the test configuration file and exposes it as structured
Type_Safe objects, replacing raw dict access everywhere.

Usage:
    from sg_send_qa.models.QA_Config import QA_Config
    cfg = QA_Config()
    print(cfg.screenshots.viewport_width)   # 1280
    print(cfg.targets.production.user_url)  # https://send.sgraph.ai
"""

import json
from pathlib import Path
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self as Type_Safe

# [LIB-2026-04-01-020] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
class QA_Config__Target(Type_Safe):
    """One test target (local or production)."""
    user_url  : str = ""
    admin_url : str = ""


class QA_Config__Targets(Type_Safe):
    """All configured test targets."""
    local      : QA_Config__Target
    production : QA_Config__Target


class QA_Config__Screenshots(Type_Safe):
    """Screenshot capture settings."""
    directory             : str   = "sg_send_qa__site/pages/use-cases"
    viewport_width        : int   = 1280
    viewport_height       : int   = 720
    visual_diff_threshold : float = 0.01


class QA_Config__Docs(Type_Safe):
    """Documentation generation settings."""
    output_directory : str = "sg_send_qa__site"
    template         : str = "default"


# [LIB-2026-04-01-021] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
class QA_Config(Type_Safe):
    """Loaded test configuration.

    Reads from tests/config/test-config.json by default.
    Pass a custom path to load from elsewhere.
    """
    targets     : QA_Config__Targets
    screenshots : QA_Config__Screenshots
    docs        : QA_Config__Docs

    _config_path: str = ""          # internal — set before first use

    def load(self, config_path: str = "") -> "QA_Config":
        """Load config from JSON file. Returns self for chaining."""
        path = Path(config_path) if config_path else self._default_path()
        if not path.exists():
            return self                 # return defaults if file not found
        raw = json.loads(path.read_text())

        t = raw.get("targets", {})
        self.targets.local.user_url        = t.get("local", {}).get("user_url", "")
        self.targets.local.admin_url       = t.get("local", {}).get("admin_url", "")
        self.targets.production.user_url   = t.get("production", {}).get("user_url", "")
        self.targets.production.admin_url  = t.get("production", {}).get("admin_url", "")

        s = raw.get("screenshots", {})
        self.screenshots.directory             = s.get("directory", self.screenshots.directory)
        self.screenshots.viewport_width        = s.get("viewport_width", self.screenshots.viewport_width)
        self.screenshots.viewport_height       = s.get("viewport_height", self.screenshots.viewport_height)
        self.screenshots.visual_diff_threshold = s.get("visual_diff_threshold", self.screenshots.visual_diff_threshold)

        d = raw.get("docs", {})
        self.docs.output_directory = d.get("output_directory", self.docs.output_directory)
        self.docs.template         = d.get("template", self.docs.template)

        return self

    @staticmethod
    def _default_path() -> Path:
        """Resolve tests/config/test-config.json relative to repo root."""
        here = Path(__file__).parent.parent.parent   # sg_send_qa/models/ → repo root
        return here / "tests" / "config" / "test-config.json"
