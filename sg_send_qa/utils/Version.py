"""Version reader for the SG/Send QA package.

Reads the version string from sg_send_qa/version at import time.
"""

from pathlib import Path
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self as Type_Safe


class Version(Type_Safe):
    FILE_NAME_VERSION: str = "version"

    def path_code_root(self) -> Path:
        import sg_send_qa.utils
        return Path(sg_send_qa.utils.__file__).parent.parent

    def path_version_file(self) -> Path:
        return self.path_code_root() / self.FILE_NAME_VERSION

    def value(self) -> str:
        version_file = self.path_version_file()
        if version_file.exists():
            return version_file.read_text().strip()
        return "v0.0.0"


version__sg_send__qa = Version().value()
