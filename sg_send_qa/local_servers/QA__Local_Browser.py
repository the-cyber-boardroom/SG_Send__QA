from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now

from osbot_utils.utils.Json                                                         import json_load_file, json_save_file
from osbot_utils.utils.Files                                                        import path_combine, file_not_exists
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from sg_send_qa.browser.for__osbot_playwright.chromium_executable_path              import chromium_executable_path
from sg_send_qa.local_servers.QA__Local_Servers                                     import QA__Local_Servers
from sgit_ai.safe_types.Safe_Str__File_Path                                         import Safe_Str__File_Path


LOCAL_BROWSER__FILE_NAME__BROWSER_CONFIG = 'browser-config.json'

class Schema__Local_Browser__Config(Type_Safe):
    chromium_executable_path: Safe_Str__File_Path = None
    last_updated_at         : Timestamp_Now

class QA__Local_Browser(Type_Safe):
    qa_local_servers : QA__Local_Servers

    def browser_config(self) -> Schema__Local_Browser__Config:
        file__browser_config = self.path__file__browser_config()
        if file_not_exists(file__browser_config):
            self.browser_config__update()

        file_data = json_load_file(file__browser_config)
        return Schema__Local_Browser__Config.from_json(file_data)

    def browser_config__update(self):
        kwargs                       = dict(chromium_executable_path = chromium_executable_path())
        browser_config               = Schema__Local_Browser__Config(**kwargs)
        file__browser_config         = self.path__file__browser_config()
        json_save_file(python_object = browser_config.json(),
                       path          = file__browser_config ,
                       pretty        = True                 )

    def chromium_executable_path(self):
        return self.browser_config().chromium_executable_path

    def path__file__browser_config(self):
        return path_combine(self.qa_local_servers.path__folder__local_servers(), LOCAL_BROWSER__FILE_NAME__BROWSER_CONFIG)