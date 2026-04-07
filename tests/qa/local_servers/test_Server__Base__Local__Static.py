from unittest                                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                  import base_types
from sg_send_qa.local_servers.Server__Base__Local                                               import Server__Base__Local
from sg_send_qa.local_servers.Server__Base__Local__Static                                       import Server__Base__Local__Static

class test_Server__Base__Local__Static(TestCase):

    def test__init__(self):
        with Server__Base__Local__Static() as _:
            assert type(_)       is Server__Base__Local__Static
            assert base_types(_) == [Server__Base__Local, Type_Safe, object]

    def test_server__popen_args(self):
        with Server__Base__Local__Static() as _:
            _.config.server__host = 'localhost'
            _.config.server__port = 7777
            _.config.ui__serve_dir = '/tmp/build'
            args = _.server__popen_args()
            assert args == ['python', '-m', 'http.server',
                            '--directory', '/tmp/build'   ,
                            '--bind'     , 'localhost'    ,
                            '7777'                        ]

    def test_server__needs_restart__not_online(self):
        with Server__Base__Local__Static() as _:
            assert _.server__needs_restart('/dir', 'hash1') is True                              # not online → needs start

    def test_server__needs_restart__same_content(self):
        with Server__Base__Local__Static() as _:
            _.config.server__online   = True
            _.config.ui__serve_dir    = '/dir'
            _.config.ui__content_hash = 'hash1'
            assert _.server__needs_restart('/dir', 'hash1') is False                             # same → no restart

    def test_server__needs_restart__different_hash(self):
        with Server__Base__Local__Static() as _:
            _.config.server__online   = True
            _.config.ui__serve_dir    = '/dir'
            _.config.ui__content_hash = 'hash1'
            assert _.server__needs_restart('/dir', 'hash2') is True                              # different hash → restart