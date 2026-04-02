import subprocess
import psutil
from osbot_fast_api.utils.Fast_API_Server                                   import Fast_API_Server
from osbot_utils.helpers.duration.decorators.print_duration                 import print_duration
from osbot_utils.testing.Stderr                                             import Stderr
from osbot_utils.testing.__helpers                                          import obj
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.utils.Http                                                 import wait_for_http, wait_for_port, url_join_safe
from osbot_utils.utils.Misc                                                 import random_port, wait_for
from osbot_utils.utils.Objects                                              import obj_dict
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                      import SG_Send__Browser__Test_Harness
from sg_send_qa.browser.Schema__Browser_Test_Config                         import Schema__Browser_Test_Config
from sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user   import run
from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import setup__send_user_lambda__test_client


class Page__Send_SGraph_Ai__Upload(Type_Safe):
    config  : Schema__Browser_Test_Config                                     # headless=True (CI default), headless=False for debug
    harness : SG_Send__Browser__Test_Harness = None                           # lifecycle owner — None until setup() is called
    sg_send = None                                                            # SG_Send__Browser__Pages — None until setup() is called

    # ═══════════════════════════════════════════════════════════════════════
    # Production path — headless=True by default, safe for CI
    # ═══════════════════════════════════════════════════════════════════════

    def setup(self):                                                          # start harness, set token, open upload page
        self.harness = SG_Send__Browser__Test_Harness(config=self.config)
        self.harness.setup()
        self.sg_send = self.harness.sg_send
        self.harness.set_access_token()
        self.sg_send.page__root()
        return self

    def upload_file(self, file_path: str) -> str:                            # upload a file and return the friendly token
        filename      = file_path.split("/")[-1]
        content_bytes = open(file_path, "rb").read()
        return self.sg_send.workflow__upload_friendly_token(
            token         = self.harness.access_token(),
            filename      = filename,
            content_bytes = content_bytes,
        )

    def get_friendly_token(self) -> str:                                     # read the current friendly token from the page
        return self.sg_send.upload__get_friendly_token()

    def teardown(self):                                                      # stop harness cleanly
        if self.harness:
            self.harness.teardown()
        return self

    # ═══════════════════════════════════════════════════════════════════════
    # Debug / performance investigation — kept for reference
    # ═══════════════════════════════════════════════════════════════════════

    def current_logic(self):
        with print_duration(action_name="setup harness"):
            self.harness = SG_Send__Browser__Test_Harness()
        with print_duration(action_name="setup chrome"):
            self.harness.setup()                                             # headless default from config (True in CI)
            self.sg_send = self.harness.sg_send
        with print_duration(action_name="set_access_token"):
            self.harness.set_access_token()
        with print_duration(action_name="open page root"):
            self.sg_send.page__root()

        with print_duration(action_name="close servers (but not chrome)"):
            self.harness.teardown()

# [LIB-2026-04-01-031] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md


    # [LIB-2026-04-01-032] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
    def debug_setup_chrome(self):
        self.harness = SG_Send__Browser__Test_Harness()
        with print_duration(action_name="setup chrome"):
            self.harness.headless(False).setup()              # headless=False intentional — debug probe only

        with print_duration(action_name="close servers (but not chrome)"):
            self.harness.teardown()

# [LIB-2026-04-01-033] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

    def debug_inner_calls_of_setup(self):
        self.harness = SG_Send__Browser__Test_Harness()
        # ---- these are the exact methods that SG_Send__Browser__Test_Harness(),setup() will call

        #with print_duration(action_name="setup SG_Send__Browser__Test_Harness"):
        with self.harness as _:
            with print_duration(action_name ="_load_saved_state"):
                saved_state =  _._load_saved_state()
            with print_duration(action_name ="_start_api_server"):
                _._start_api_server(saved_state)
            with print_duration(action_name ="_build_ui"):
                _._build_ui(saved_state)
            with print_duration(action_name ="_start_ui_server"):
                _._start_ui_server(saved_state)
            with print_duration(action_name ="_create_browser"):
                _._create_browser()
            with print_duration(action_name ="_save_state"):
                _._save_state()
            with print_duration(action_name ="capture_stderr"):
                if _.config.capture_stderr:
                    _.stderr = Stderr()
                    _.stderr.start()

        self.harness.teardown()

# [LIB-2026-04-01-034] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

    def debug_start_api_server(self):
        with SG_Send__Browser__Test_Harness() as _:
            assert _.config.headless is True                                # this will disable the use of safe state
            assert _._load_saved_state() is None                            # confirm that save state is disabled by default
            with print_duration(action_name="start api server"):
                _._start_api_server()
            with print_duration(action_name="stop api server"):
                _.api_server.stop()

    # [LIB-2026-04-01-035] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

    def debug_start_api_server__with_saved_state(self):
        config = Schema__Browser_Test_Config(headless=False)        # [LIB-2026-04-01-036] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
        with SG_Send__Browser__Test_Harness(config=config) as _:
            with print_duration(action_name="load_saved_state"):
                saved_state = _._load_saved_state()                 # [LIB-2026-04-01-037] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

                #saved_state.print_obj()
                #print(_.persistence.state_file())
                # [LIB-2026-04-01-038] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md


            with print_duration(action_name="start api server"):
                _._start_api_server(saved_state=saved_state)
            with print_duration(action_name="stop api server"):
                _.api_server.stop()


    def debug_inner_methods_of__start_api_server(self):

        with SG_Send__Browser__Test_Harness() as _:
            saved_state     = _._load_saved_state()                     # this is passed as a param to start_api_server
            with print_duration(action_name="setup__send_user_lambda__test_client"):
                self.test_objs  = setup__send_user_lambda__test_client()

            with print_duration(action_name="setup Fast_API_Server"):
                api_port        = saved_state.api_port if saved_state else 0            # 0 = let Fast_API_Server pick random
                self.api_server = Fast_API_Server(app  = self.test_objs.fast_api__app ,
                                                  port = api_port                      )

            with print_duration(action_name="start api server"):
                self.api_server.start()

            with print_duration(action_name="stop api server"):
                self.api_server.stop()

        # [LIB-2026-04-01-039] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

    # [LIB-2026-04-01-040] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
    def debug__start_and_stop_server_using_port(self):
        import os
        import requests
        from subprocess import check_output
        def get_process_details(pid):
            try:
                proc = psutil.Process(pid)
                mem_info, cpu_info, io_info, status = proc.memory_info(), proc.cpu_times(), proc.io_counters(), proc.status()
                return {
                    "pid": pid,
                    "name": proc.name(),
                    "mem_info": mem_info,
                    "cpu_info": cpu_info,
                    "io_info": io_info,
                    "status": status,
                }
            except psutil.NoSuchProcess:
                return {"error": "Process not found"}

        port              = random_port()
        fast_api_handler  = run.__module__
        handler_app       = f"{fast_api_handler}:app"
        process__name = ["poetry"]
        process__args = ["run",
                         "uvicorn",
                         handler_app      ,
                         "--port", str(port),
                         '--log-level', 'info',
                         '--timeout-graceful-shutdown', '0']

        popen_args         = process__name + process__args
        # stderr             = Stderr()                           # create object to capture stderr
        # stderr.start()                                          # start monitoring
        stderr             = subprocess.PIPE
        stdout             = subprocess.PIPE
        fast_api_process   = subprocess.Popen(popen_args,
                                              stderr = stderr ,
                                              stdout = stdout)

        url__server = f"http://localhost:{port}"
        url__server__info = url_join_safe(url__server, "/info/status")

        with print_duration(): # this is about ~ 1.35 seconds
            if not wait_for_port('localhost', port):
                raise Exception(f"was not able to get port {port} in localhost")

        with print_duration():      # this is about ~ 0.017 seconds
            if not wait_for_http(url__server__info):
                raise Exception(f"was not able to open url: {url__server__info}")


        pid = fast_api_process.pid

        result = dict(fast_api_process  = obj_dict(fast_api_process) ,
                      stderr            = stderr                     ,
                      stdout            = stdout                     ,
                      pid               = pid                        ,
                      port              = port                       ,
                      url__server       = url__server                ,
                      url__server__info = url__server__info          )

        return obj(result)

        details = get_process_details(int(pid))
        if "error" not in details:
            print("\nFastAPI process details:")
            for key, value in details.items():
                if isinstance(value, dict):
                    sub_keys = [k for k in value]
                    sub_values = [str(v) for v in value[sub_keys]]
                    print(f"{key}: {', '.join(sub_values)}")
                else:
                    print(f"{key}: {value}")
            os.system(f"kill {pid}")
        else:
            print(details["error"])
