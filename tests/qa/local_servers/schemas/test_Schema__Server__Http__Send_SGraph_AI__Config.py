from unittest                                                                      import TestCase
from sg_send_qa.local_servers.schemas.Schema__Server__Http__Send_SGraph_AI__Config import Schema__Server__Http__Send_SGraph_AI__Config


class test_Schema__Server__Http__Send_SGraph_AI__Config(TestCase):

    def test__init__(self):
        with Schema__Server__Http__Send_SGraph_AI__Config() as _:
            assert type(_)          is Schema__Server__Http__Send_SGraph_AI__Config
            assert _.server__port   == 50002                                                       # project-specific default

    def test_inherits_static_fields(self):
        with Schema__Server__Http__Send_SGraph_AI__Config() as _:
            assert _.health_check__http__path == '/'                                             # from Static base
            assert _.ui__serve_dir            == None                                              # from Static base
