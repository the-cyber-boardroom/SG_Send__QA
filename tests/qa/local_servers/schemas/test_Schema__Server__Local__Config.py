from unittest                                                       import TestCase
from osbot_utils.testing.__                                         import __
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.utils.Objects                                      import base_types
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Config import Schema__Server__Local__Config


class test_Schema__Server__Local__Config(TestCase):

    def test__init__(self):
        with Schema__Server__Local__Config() as _:
            assert type(_)       is Schema__Server__Local__Config
            assert base_types(_) == [Type_Safe, object]
            assert _.obj()       == __(health_check__port__last_status    = None       ,
                                       health_check__port__last_timestamp = None       ,
                                       server__host                       = 'localhost',
                                       server__online                     = False      ,
                                       server__port                       = None       ,         # no default port on base
                                       server__scheme                     = 'http'     ,
                                       server__process_id                 = None       ,
                                       server__started                    = False      ,
                                       server__stopped                    = False      )
