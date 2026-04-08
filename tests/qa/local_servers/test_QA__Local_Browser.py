from unittest                                   import TestCase
from osbot_utils.testing.__                     import __, __NOT_NONE__, __SKIP__
from osbot_utils.utils.Files                    import parent_folder_name, file_name
from sg_send_qa.local_servers.QA__Local_Browser import QA__Local_Browser


class test_QA__Local_Browser(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.local_browser = QA__Local_Browser()

    def test_browser_config(self):
        with self.local_browser as _:
            browser_config = _.browser_config()
            assert browser_config.obj() == __(chromium_executable_path = __NOT_NONE__,        # make sure value is set
                                              last_updated_at          = __SKIP__   )

    def test_path__file__browser_config(self):
        with self.local_browser as _:
            file__browser_config = _.path__file__browser_config()
            print()
            assert parent_folder_name(file__browser_config                       ) == '.local-servers'
            assert file_name         (file__browser_config, check_if_exists=False) == 'browser-config.json'
