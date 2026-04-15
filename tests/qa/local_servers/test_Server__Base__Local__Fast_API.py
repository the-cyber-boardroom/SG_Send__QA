from unittest                                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                  import base_types
from sg_send_qa.local_servers.Server__Base__Local                                               import Server__Base__Local
from sg_send_qa.local_servers.Server__Base__Local__Fast_API                                     import Server__Base__Local__Fast_API


class test_Server__Base__Local__Fast_API(TestCase):

    def test__init__(self):
        with Server__Base__Local__Fast_API() as _:
            assert type(_)       is Server__Base__Local__Fast_API
            assert base_types(_) == [Server__Base__Local, Type_Safe, object]

    def test_server__popen_args(self):
        import sys
        with Server__Base__Local__Fast_API() as _:
            _.config.fastapi__handler = 'my_app.module:app'
            _.config.server__port     = 9999
            args = _.server__popen_args()
            assert args[0]    == sys.executable                # uses same Python as test runner
            assert args[1:3]  == ['-m', 'uvicorn']
            assert 'my_app.module:app' in args
            assert '9999'              in args

    def test_url__for_health_check(self):
        with Server__Base__Local__Fast_API() as _:
            _.config.server__port = 8080
            assert _.url__for_health_check() == 'http://localhost:8080/info/status'
