import sg_send_qa
from typing                                                                       import Type
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                    import type_safe
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                 import Safe_Id
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path
from osbot_utils.utils.Files                                                      import path_combine, create_folder, path_combine_safe, file_exists, file_delete
from osbot_utils.utils.Json                                                       import json_save_file, json_load_file

DEFAULT_FOLDER__QA__LOCAL_SERVERS  = '../.local-servers'
DEFAULT_FOLDER__QA__SERVER_CONFIGS = 'server-configs'

class QA__Local_Servers(Type_Safe):
    base_folder : Safe_Str__File__Path  = sg_send_qa.path                        # this allows choosing another folder as root

    def path__folder__local_servers(self)  -> Safe_Str__File__Path:
        return path_combine(self.base_folder, DEFAULT_FOLDER__QA__LOCAL_SERVERS)

    def path__folder__server_configs(self) -> Safe_Str__File__Path:
        return path_combine(self.path__folder__local_servers(), DEFAULT_FOLDER__QA__SERVER_CONFIGS)

    def path__file__server_config(self, server_id: Safe_Id ) -> Safe_Str__File__Path:
        server_config__file_name = f'{server_id}.json'
        server_config__file_path = path_combine_safe(self.path__folder__server_configs(), server_config__file_name)
        return server_config__file_path

    # todo: refactor all this server_config logic into separate class

    @type_safe
    def server_config__delete(self, server_id: Safe_Id):
        if self.server_config__exists(server_id):
            server_config__file_path =self.path__file__server_config(server_id)
            return file_delete(server_config__file_path)
        return False
    @type_safe
    def server_config__exists(self, server_id: Safe_Id):
        server_config__file_path =self.path__file__server_config(server_id)
        return file_exists(server_config__file_path)

    @type_safe
    def server_config__load(self, server_id: Safe_Id, config_class: Type[Type_Safe]):
        server_config__file_path =self.path__file__server_config(server_id)
        if file_exists(server_config__file_path):
            json_data     = json_load_file(server_config__file_path)
            server_config =  config_class.from_json(json_data)
        else:
            server_config = config_class()                                                  # if it doesn't exist create an empty one (this way we always have a valid object
            self.server_config__save(server_id=server_id, server_config=server_config)

        return server_config

    @type_safe
    def server_config__save(self                    ,
                            server_id    : Safe_Id  ,
                            server_config: Type_Safe
                       ) -> bool:
        self.setup()                                                                            # idempotent: ensure .local-servers/server-configs/ exists before write
        server_config__file_path     = self.path__file__server_config(server_id)
        json_data                    = server_config.json()
        json_save_file(python_object = json_data                ,
                       path          = server_config__file_path ,
                       pretty        = True                     )
        return self.server_config__exists(server_id)

    def setup(self):
        create_folder(self.path__folder__local_servers   ())      # this will create the folders if they don't exist
        create_folder(self.path__folder__server_configs())
        return self