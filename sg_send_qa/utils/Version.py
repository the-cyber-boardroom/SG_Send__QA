from pathlib import Path


class Version:
    FILE_NAME_VERSION = 'version'

    def path_code_root(self):
        import sg_send_qa.utils
        return Path(sg_send_qa.utils.__file__).parent.parent

    def path_version_file(self):
        return self.path_code_root() / self.FILE_NAME_VERSION

    def value(self):
        version_file = self.path_version_file()
        if version_file.exists():
            return version_file.read_text().strip()
        return 'v0.0.0'


version__sg_send__qa = Version().value()
