from unittest                                               import TestCase

import sg_send_qa
from osbot_utils.testing.Temp_Folder                        import Temp_Folder
from osbot_utils.utils.Misc                                 import random_port
from osbot_utils.testing.__                                 import __, __SKIP__
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
            assert _.obj()  == __(config=__(fastapi__handler='sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user:app',
                                             health_check__api__path='/info/status',
                                             health_check__api__last_status=None,
                                             health_check__api__last_timestamp=None,
                                             health_check__api__last_response=None,
                                             health_check__port__last_status=None,
                                             health_check__port__last_timestamp=None,
                                             server__host='localhost',
                                             server__is_fast_api=True,
                                             server__online=False,
                                             server__port=50001,
                                             server__scheme='http',
                                             server__process_id=None,
                                             server__started=False,
                                             server__stopped=False),
                                   qa_local_servers=__(base_folder=sg_send_qa.path))

    def test_server__start____stop(self):
        with Temp_Folder() as temp_folder:
            temp_port                               = random_port()
            with Server__API__Send_SGraph_AI() as _:                                         # for these test use a new object so that we don't interfere with the current values
                _.qa_local_servers.base_folder = temp_folder.full_path              # first set the folder
                _.qa_local_servers.setup()                                          # this will create the temp folders
                _.config.server__port          = temp_port                          # then the port
                _.config__save()                                                    # todo: refactor this 'set custom.temp folder and port' flow , since this is also a common method

                #_.config__update()                                                  #
                assert _.server__start() is True

                assert _.config.obj() == __(fastapi__handler='sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user:app',
                                            health_check__api__path='/info/status',
                                            health_check__api__last_status=True,
                                            health_check__api__last_timestamp=__SKIP__,
                                            health_check__api__last_response=__(name='osbot_fast_api_serverless',
                                                                                version=__SKIP__,
                                                                                status='operational',
                                                                                environment='local'),
                                            health_check__port__last_status=True,
                                            health_check__port__last_timestamp=__SKIP__,
                                            server__host='localhost',
                                            server__is_fast_api=True,
                                            server__online=True,
                                            server__port=temp_port,
                                            server__scheme='http',
                                            server__process_id=__SKIP__,
                                            server__started=True,
                                            server__stopped=False)

                assert _.server__stop() is True

                assert _.config.obj() == __(fastapi__handler='sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user:app',
                                            health_check__api__path='/info/status',
                                            health_check__api__last_status=False,
                                            health_check__api__last_timestamp=None,
                                            health_check__api__last_response=None,
                                            health_check__port__last_status=False,
                                            health_check__port__last_timestamp=None,
                                            server__host='localhost',
                                            server__is_fast_api=True,
                                            server__online=False,
                                            server__port=temp_port,
                                            server__scheme='http',
                                            server__process_id=None,
                                            server__started=False,
                                            server__stopped=True)

            #assert _.config.obj() == __()

    # def test_server__stop(self):
    #     with self.api_server as _:
    #         assert _.server__stop() is False

    # def test_update_status(self):
    #     with self.api_server as _:
    #         _.config__update()
    #         # todo: add assert of data we know changes here

