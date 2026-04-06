from unittest                                                       import TestCase
from osbot_utils.testing.__                                         import __
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id   import Safe_Id
from osbot_utils.utils.Files                                        import parent_folder_name, folder_name, folder_exists
from sg_send_qa.local_servers.QA__Local_Servers                     import QA__Local_Servers

class test_QA__Local_Servers(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.qa_local_servers = QA__Local_Servers()

    def test__init__(self):
        with self.qa_local_servers as _:
            assert type(_) is QA__Local_Servers

    def test_path__folder__base(self):
        with self.qa_local_servers as _:
            assert parent_folder_name(_.path__folder__local_servers()) == 'SG_Send__QA'
            assert folder_name       (_.path__folder__local_servers()) == '.local-servers'

    def test_server_config__load(self):
        class Schema__An_Config(Type_Safe):
            answer: Safe_Id

        with self.qa_local_servers as _:
            server__id          = 'an-server'
            server__config_data = Schema__An_Config(answer= 42 )
            assert type(_.server_config__load(server__id, Schema__An_Config))   is Schema__An_Config
            assert _.server_config__exists(server__id)                          is True
            assert _.server_config__delete(server__id)                          is True

            assert _.server_config__save(server__id, server__config_data)       is True
            assert _.server_config__exists(server__id)                          is True

            server_config = _.server_config__load(server__id, Schema__An_Config)

            assert type(server_config)                                    is Schema__An_Config
            assert server_config.obj()                                    == __(answer='42')
            assert _.server_config__delete(server__id)                    is True
            assert _.server_config__delete(server__id)                    is False



    def test_setup(self):
        with self.qa_local_servers as _:
            assert _.setup()                                       is self.qa_local_servers
            assert folder_exists(_.path__folder__local_servers          ()) is True
            assert folder_exists(_.path__folder__server_configs()) is True

