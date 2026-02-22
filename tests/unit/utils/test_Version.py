from sg_send_qa.utils.Version import Version, version


class TestVersion:

    def test_value(self):
        v = Version()
        assert v.value().startswith('v')

    def test_version_module_level(self):
        assert version == 'v0.1.0'

    def test_path_version_file_exists(self):
        v = Version()
        assert v.path_version_file().exists()

    def test_path_code_root(self):
        v = Version()
        assert v.path_code_root().name == 'sg_send_qa'
