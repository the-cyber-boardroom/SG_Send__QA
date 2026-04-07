from unittest                                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                  import base_types
from sg_send_qa.local_servers.Server__Base__Local                                               import Server__Base__Local



# ═══════════════════════════════════════════════════════════════════════════════
# Base class tests — structure and inheritance
# ═══════════════════════════════════════════════════════════════════════════════

class test_Server__Base__Local(TestCase):

    def test__init__(self):
        with Server__Base__Local() as _:
            assert type(_)       is Server__Base__Local
            assert base_types(_) == [Type_Safe, object]

    def test_server__is_running__no_pid(self):
        with Server__Base__Local() as _:
            assert _.server__is_running() is False                                               # no PID → not running

    def test_url__for_server(self):
        with Server__Base__Local() as _:
            _.config.server__scheme = 'http'
            _.config.server__host   = 'localhost'
            _.config.server__port   = 12345
            assert _.url__for_server()            == 'http://localhost:12345'
            assert _.url__for_server('/health')   == 'http://localhost:12345/health'
            assert _.url__for_server('health')    == 'http://localhost:12345/health'              # auto-adds leading /

    def test_server__popen_args__raises(self):
        with Server__Base__Local() as _:
            with self.assertRaises(NotImplementedError):
                _.server__popen_args()





