from unittest                                               import TestCase
from osbot_utils.testing.__                                 import __
from osbot_utils.utils.Dev                                  import pprint
from sg_send_qa.local_servers.Server__API__Send_SGraph_AI   import Server__API__Send_SGraph_AI, Schema__Server__API__Send_SGraph_AI__Config


class test_Server__API__Send_SGraph_AI(TestCase):

    @classmethod
    def setUpClass(cls):
        # todo: add support for starting the server in a different port and using a different folder
        #       so that we can fully test this workflow here
        cls.api_server = Server__API__Send_SGraph_AI()

    def test__init__(self):
        with self.api_server as _:
            assert type(_) is Server__API__Send_SGraph_AI
            assert _.obj()  == __(port=50001)

    def test_server_details(self):
        with self.api_server as _:
            server_details = _.server_details()
            assert type(server_details) is Schema__Server__API__Send_SGraph_AI__Config

    def test_server__start(self):
        with self.api_server as _:

            # todo: add check when server is already live
            result = _.server__start()
            pid = 38258                 # todo: replace with captured value

            _.config.print_obj()

            #result.print_obj()                                      # @qa this is a nice trick when developing the code to see that is returned (and to collect the variables/data for the assert)

    def test_server__stop(self):
        with self.api_server as _:
            _.server__stop()

    def test_update_status(self):
        with self.api_server as _:
            _.update_status()
            # todo: add assert of data we know changes here

