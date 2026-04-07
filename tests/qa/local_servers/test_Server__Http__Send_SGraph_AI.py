# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Server__Http__Send_SGraph_AI
# Mirrors test_Server__API__Send_SGraph_AI structure
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                   import TestCase
import sg_send_qa
from osbot_utils.testing.Temp_Folder                                                            import Temp_Folder
from osbot_utils.testing.__                                                                     import __, __SKIP__
from osbot_utils.utils.Files                                                                    import file_create, path_combine
from osbot_utils.utils.Misc                                                                     import random_port
from sg_send_qa.local_servers.Server__Http__Send_SGraph_AI                                      import Server__Http__Send_SGraph_AI, SEND_SGRAPH_AI__FILE_ID__HTTP_SERVER_CONFIG

class test_Server__Http__Send_SGraph_AI(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.http_server = Server__Http__Send_SGraph_AI()

    def test__init__(self):
        with self.http_server as _:
            assert type(_) is Server__Http__Send_SGraph_AI
            assert _.obj() == __(config    = __(health_check__port__last_status    = None ,
                                                health_check__port__last_timestamp = None ,
                                                server__host                       = 'localhost',
                                                server__online                     = False ,
                                                server__port                       = 50002 ,
                                                server__scheme                     = 'http',
                                                server__process_id                 = None  ,
                                                server__started                    = False ,
                                                server__stopped                    = False ,
                                                health_check__http__path           = '/'   ,
                                                health_check__http__last_status    = None  ,
                                                health_check__http__last_timestamp = None  ,
                                                ui__serve_dir                      = None  ,
                                                ui__content_hash                   = None  ),
                                 qa_local_servers = __(base_folder = sg_send_qa.path)      ,
                                 server_id        = SEND_SGRAPH_AI__FILE_ID__HTTP_SERVER_CONFIG)

    def test_server__start____stop(self):
        with Temp_Folder() as temp_folder:
            temp_port = random_port()

            # create a minimal index.html so the health check has something to serve
            serve_dir = temp_folder.full_path
            file_create(path     = path_combine(serve_dir, 'index.html'),
                        contents = '<html><body>ok</body></html>'       )

            with Server__Http__Send_SGraph_AI() as _:
                _.qa_local_servers.base_folder = temp_folder.full_path
                _.qa_local_servers.setup()

                _.config.ui__serve_dir         = serve_dir                      # todo: find a better way to assign these values
                _.config.ui__content_hash      = 'abc12345'
                _.config.server__port          = temp_port
                _.config__save()

                assert _.server__start() is True

                assert _.config.obj() == __(health_check__port__last_status    = True       ,
                                            health_check__port__last_timestamp = __SKIP__   ,
                                            server__host                       = 'localhost',
                                            server__online                     = True       ,
                                            server__port                       = temp_port  ,
                                            server__scheme                     = 'http'     ,
                                            server__process_id                 = __SKIP__   ,
                                            server__started                    = True       ,
                                            server__stopped                    = False      ,
                                            health_check__http__path           = '/'        ,
                                            health_check__http__last_status    = True       ,
                                            health_check__http__last_timestamp = __SKIP__   ,
                                            ui__serve_dir                      = serve_dir  ,
                                            ui__content_hash                   = 'abc12345' )

                assert _.server__stop() is True

                assert _.config.obj() == __(health_check__port__last_status    = False      ,
                                            health_check__port__last_timestamp = None       ,
                                            server__host                       = 'localhost',
                                            server__online                     = False      ,
                                            server__port                       = temp_port  ,
                                            server__scheme                     = 'http'     ,
                                            server__process_id                 = None       ,
                                            server__started                    = False      ,
                                            server__stopped                    = True       ,
                                            health_check__http__path           = '/'        ,
                                            health_check__http__last_status    = False      ,
                                            health_check__http__last_timestamp = None       ,
                                            ui__serve_dir                      = serve_dir  ,
                                            ui__content_hash                   = 'abc12345' )

    def test_server__needs_restart(self):
        with Server__Http__Send_SGraph_AI() as _:
            assert _.server__needs_restart(ui_serve_dir    = '/some/dir',
                                           ui_content_hash = 'aaa11111' ) is True              # not online → needs start

            _.config.server__online    = True
            _.config.ui__serve_dir     = '/some/dir'
            _.config.ui__content_hash  = 'aaa11111'
            assert _.server__needs_restart(ui_serve_dir    = '/some/dir',
                                           ui_content_hash = 'aaa11111' ) is False             # same content → no restart

            assert _.server__needs_restart(ui_serve_dir    = '/other/dir',
                                           ui_content_hash = 'aaa11111'  ) is True             # different dir → restart

            assert _.server__needs_restart(ui_serve_dir    = '/some/dir',
                                           ui_content_hash = 'bbb22222' ) is True              # different hash → restart
