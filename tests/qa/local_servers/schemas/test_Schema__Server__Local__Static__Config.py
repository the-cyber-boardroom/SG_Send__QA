from unittest                                                               import TestCase
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.utils.Objects                                              import base_types
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Config         import Schema__Server__Local__Config
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Static__Config import Schema__Server__Local__Static__Config


class test_Schema__Server__Local__Static__Config(TestCase):

    def test__init__(self):
        with Schema__Server__Local__Static__Config() as _:
            assert type(_)       is Schema__Server__Local__Static__Config
            assert base_types(_) == [Schema__Server__Local__Config, Type_Safe, object]
            assert _.health_check__http__path       == '/'
            assert _.health_check__http__last_status is None
            assert _.ui__serve_dir                  is None
            assert _.ui__content_hash               is None
