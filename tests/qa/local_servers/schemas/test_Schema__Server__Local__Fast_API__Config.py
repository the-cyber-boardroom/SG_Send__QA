from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Objects                                                  import base_types
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Config             import Schema__Server__Local__Config
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Fast_API__Config   import Schema__Server__Local__Fast_API__Config


class test_Schema__Server__Local__Fast_API__Config(TestCase):

    def test__init__(self):
        with Schema__Server__Local__Fast_API__Config() as _:
            assert type(_)                              is Schema__Server__Local__Fast_API__Config
            assert base_types(_)                        == [Schema__Server__Local__Config, Type_Safe, object]
            assert _.health_check__api__path            == '/info/status'
            assert _.health_check__api__last_status     is None
            assert _.health_check__api__last_response   is None

    def test_inherits_base_fields(self):
        with Schema__Server__Local__Fast_API__Config() as _:
            assert _.server__host                      == 'localhost'                                               # from base
            assert _.server__scheme                    == 'http'                                                    # from base

