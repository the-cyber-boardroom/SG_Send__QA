from unittest                                                                     import TestCase
from sg_send_qa.local_servers.schemas.Schema__Server__API__Send_SGraph_AI__Config import Schema__Server__API__Send_SGraph_AI__Config


class test_Schema__Server__API__Send_SGraph_AI__Config(TestCase):

    def test__init__(self):
        with Schema__Server__API__Send_SGraph_AI__Config() as _:
            assert type(_)       is Schema__Server__API__Send_SGraph_AI__Config
            assert _.server__port        == 50001                                                # project-specific default
            assert _.server__is_fast_api is True

    def test_inherits_fast_api_fields(self):
        with Schema__Server__API__Send_SGraph_AI__Config() as _:
            assert _.health_check__api__path == '/info/status'                                   # from FastAPI base
            assert _.server__host            == 'localhost'                                       # from base