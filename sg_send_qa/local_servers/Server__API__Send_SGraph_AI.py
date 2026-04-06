import os
import subprocess

import requests
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                            import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id import Safe_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.network.safe_uint.Safe_UInt__Port import Safe_UInt__Port
from osbot_utils.type_safe.primitives.domains.python.safe_str.Safe_Str__Python__Qualified_Name import Safe_Str__Python__Qualified_Name
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url__Path import Safe_Str__Url__Path
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                  import type_safe
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Http                                                     import is_port_open, url_join_safe, wait_for_port
from osbot_utils.utils.Process import stop_process

from sg_send_qa.browser.for__osbot_utils.Safe_Str__Url__Host                    import Safe_Str__Url__Host
from sg_send_qa.local_servers.QA__Local_Servers                                 import QA__Local_Servers
from sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user       import run

SEND_SGRAPH_AI__SERVER__PORT      = Safe_UInt__Port          (50001)               # @dev: move to common config location # making this fixed since we shouldn't really have many copies of this running at the same time
SEND_SGRAPH_AI__SERVER__HOST      = Safe_Str__Url__Host      ('localhost')
SEND_SGRAPH_AI__SERVER__SCHEME    = Safe_Id                  ('http')               # @dev: I think an Enum would be better here
SEND_SGRAPH_AI__SERVER__MODULE    = Safe_Str__Python__Qualified_Name(run.__module__)
SEND_SGRAPH_AI__FILE_ID__SERVER_CONFIG = 'api__send-sgraph-ai'

SERVER__API__SEND_SGRAPH_AI__PATH__HEALTH_CHECK = '/info/status'

class Schema__Server__API__Send_SGraph_AI__Config(Type_Safe):
    #fastapi__module      : Safe_Str__Python__Qualified_Name    = f"{DEFAULT__SERVER__API__SEND_SGRAPH_AI__MODULE}"         # @dev add an Safe_Str for FastApi handler ref
    fastapi__handler                   : str                     = f"{SEND_SGRAPH_AI__SERVER__MODULE}:app"     # @dev add an Safe_Str for FastApi handler ref
    # todo: refactor these health_checks into separate class
    health_check__api__path            : Safe_Str__Url__Path     = SERVER__API__SEND_SGRAPH_AI__PATH__HEALTH_CHECK
    health_check__api__last_status     : bool                    = None
    health_check__api__last_timestamp  : Timestamp_Now           = None
    health_check__api__last_response   : dict                    = None
    health_check__port__last_status    : bool                    = None
    health_check__port__last_timestamp : Timestamp_Now           = None
    server__host                       : Safe_Str__Url__Host     = SEND_SGRAPH_AI__SERVER__HOST
    server__is_fast_api                : bool                    = True
    server__online                     : bool                    = False
    server__port                       : Safe_UInt__Port         = SEND_SGRAPH_AI__SERVER__PORT
    server__scheme                     : Safe_Id                 = SEND_SGRAPH_AI__SERVER__SCHEME
    server__process_id                 : Safe_UInt               = None                                                      # @dev: see what is a better Safe_* class to use here (we should have one that only contains valid process id values)
    server__started                    : bool                    = False

class Server__API__Send_SGraph_AI(Type_Safe):
    config           : Schema__Server__API__Send_SGraph_AI__Config
    qa_local_servers : QA__Local_Servers

    def is_server_running(self):
        return is_port_open(port = self.config.server__port,
                            host = self.config.server__host)

    # def process_details(self):
    #     pid = self.config.server__process_id
    #     if pid:
    #         try:
    #             proc = psutil.Process(pid)
    #             mem_info, cpu_info, io_info, status = proc.memory_info(), proc.cpu_times(), proc.io_counters(), proc.status()
    #             return {                                # todo: @dev refactor to Schema_* class
    #                 "pid": pid,
    #                 "name": proc.name(),
    #                 "mem_info": mem_info,
    #                 "cpu_info": cpu_info,
    #                 "io_info": io_info,
    #                 "status": status,
    #             }
    #         except psutil.NoSuchProcess:
    #             return {"error": "Process not found"}       # tood: @dev this should return the same Schema_* class as above

    def config__load(self):
        self.config = self.qa_local_servers.server_config__load(server_id    = SEND_SGRAPH_AI__FILE_ID__SERVER_CONFIG,
                                                                config_class = Schema__Server__API__Send_SGraph_AI__Config)
        return self

    def config__print(self):
        self.config.print_obj()
        return self

    def config__save(self):
        self.qa_local_servers.server_config__save(server_id     = SEND_SGRAPH_AI__FILE_ID__SERVER_CONFIG,
                                                  server_config = self.config)
        return self

    def update_status(self):
        with self  as _:
            _.config__load()                    # reload data
            _.health_check__port()              # run multiple updates
            _.health_check__api ()
            _.config__save()                    # save data                 # note: this is a good example of something that we could simplify with a context with the config and upload logic placed in a different class (important as we add multiple servers)
            _.config__print()
        return self
        #with self.config as _:



    #def update___server_online(self):
    def health_check__port(self):
        with self.config as _:
            if _.server__process_id:
                if is_port_open(host=self.config.server__host, port=self.config.server__port):
                    _.health_check__port__last_status    = True
                    _.health_check__port__last_timestamp = Timestamp_Now()
                    return True
                else:
                    _.health_check__port__last_status    = False
                    _.health_check__port__last_timestamp = None
                    return False

    def health_check__api(self):
        with self.config as _:
            if _.server__port:
                url = self.url__for_server(_.health_check__api__path)
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        _.health_check__api__last_status    = True
                        _.health_check__api__last_response  = response.json()
                        _.health_check__api__last_timestamp = Timestamp_Now()
                        return True
                except requests.exceptions.ConnectionError:
                    pass

                _.health_check__api__last_status    = False
                _.health_check__api__last_response  = None
                _.health_check__api__last_timestamp = None
            return False

    def url__for_server(self, path):
        with self.config as _:
            url = f"{_.server__scheme}://{_.server__host}:{_.server__port}/{path}"
            return url


    # todo: wire in these checks
    #         raise Exception(f"was not able to get port {port} in localhost")
    #url__server = f"http://localhost:{port}"
    #        url__server__info = url_join_safe(url__server, "/info/status")


    def server__is_running(self):
        with self.config as _:
            pid = _.server__process_id
            if pid:
                try:
                    os.kill(pid, 0)                 # this doesn't kill the process, just raises an exception if it doesn't exist
                    return True
                except OSError:
                    return False
            return False


    def server__start(self):
        self.config__load()         # todo: add context support here so that we don't need to always have to have both .config__load() and .config__save() in cases like this
        with self.config as _:
            _.server__online = self.is_server_running()
            if _.server__online is False:
                print("Creating server")
                port         = _.server__port
                handler_app  = _.fastapi__handler
                process__name = ["poetry"]
                process__args = ["run",
                                 "uvicorn",
                                 handler_app      ,
                                 "--port", str(port),
                                 '--log-level', 'info',
                                 '--timeout-graceful-shutdown', '0']
                popen_args           = process__name + process__args
                new_process          = subprocess.Popen(popen_args,
                                                        stderr = subprocess.PIPE ,
                                                        stdout = subprocess.PIPE
                                                        )
                _.server__process_id = new_process.pid
                #pprint(obj_dict(new_process))

                url__server = f"http://localhost:{port}"
                url__server__info = url_join_safe(url__server, "/info/status")

                # with print_duration(): # this is about ~ 1.35 seconds
                #     if not wait_for_port('localhost', port):
                #         raise Exception(f"was not able to get port {port} in localhost")
            else:
                print("Server existed")

            # pprint(new_process.stderr.readline())
            # pprint(new_process.stdout.readline())

        self.config__save()
        return self

    def server__stop(self):
        self.config__load()
        with self.config as _:
            if self.server__is_running():
                result = stop_process(_.server__process_id)
                print("server stop", result)                    # todo: add option to wait for port to be closed
                _.server__online = False
                _.server__process_id = None

                return True
            else:
                return False

            pprint(result)

        self.config__save()
        import os
        import requests
        from subprocess import check_output

        #
        #


        #
        # popen_args         = process__name + process__args
        # # stderr             = Stderr()                           # create object to capture stderr
        # # stderr.start()                                          # start monitoring
        # stderr             = subprocess.PIPE
        # stdout             = subprocess.PIPE
        # fast_api_process   = subprocess.Popen(popen_args,
        #                                       stderr = stderr ,
        #                                       stdout = stdout)
        #
        # url__server = f"http://localhost:{port}"
        # url__server__info = url_join_safe(url__server, "/info/status")
        #
        # with print_duration(): # this is about ~ 1.35 seconds
        #     if not wait_for_port('localhost', port):
        #         raise Exception(f"was not able to get port {port} in localhost")
        #
        # with print_duration():      # this is about ~ 0.017 seconds
        #     if not wait_for_http(url__server__info):
        #         raise Exception(f"was not able to open url: {url__server__info}")
        #
        #
        # pid = fast_api_process.pid
        #
        # result = dict(fast_api_process  = obj_dict(fast_api_process) ,
        #               stderr            = stderr                     ,
        #               stdout            = stdout                     ,
        #               pid               = pid                        ,
        #               port              = port                       ,
        #               url__server       = url__server                ,
        #               url__server__info = url__server__info          )
        #
        # return obj(result)