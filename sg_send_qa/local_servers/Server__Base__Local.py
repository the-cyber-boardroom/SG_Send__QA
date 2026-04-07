# ═══════════════════════════════════════════════════════════════════════════════
# Server__Base__Local — Common lifecycle for subprocess-managed local servers
# Handles PID tracking, port checks, config persistence, start/stop
# ═══════════════════════════════════════════════════════════════════════════════

import os
import signal
import subprocess
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                 import Safe_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now  import Timestamp_Now
from osbot_utils.utils.Http                                                       import is_port_open, wait_for_port, wait_for_port_closed
from osbot_utils.utils.Process                                                    import stop_process
from sg_send_qa.local_servers.QA__Local_Servers                                   import QA__Local_Servers
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Config               import Schema__Server__Local__Config


class Server__Base__Local(Type_Safe):                                                            # base class for all managed local servers
    config           : Schema__Server__Local__Config                                             # override in subclass with specific schema
    qa_local_servers : QA__Local_Servers
    server_id        : Safe_Id                                                                   # config file id (e.g. 'api__send-sgraph-ai')

    # ═══════════════════════════════════════════════════════════════════════════
    # Config persistence
    # ═══════════════════════════════════════════════════════════════════════════

    def config_class(self):                                                                      # override in subclass to return the correct schema class
        return Schema__Server__Local__Config

    def config__load(self):
        self.config = self.qa_local_servers.server_config__load(server_id    = self.server_id  ,
                                                                config_class = self.config_class())
        return self

    def config__save(self):
        self.qa_local_servers.server_config__save(server_id     = self.server_id,
                                                  server_config = self.config   )
        return self

    def config__set_server_status(self):                                                         # override in subclass to add extra health checks
        with self.config as _:
            if _.health_check__port__last_status:
                _.server__online = True
            else:
                _.server__online  = False
                _.server__started = False
        return self

    def config__update(self):
        with self as _:
            _.config__load()
            _.health_check__port()
            _.health_check__service()
            _.config__set_server_status()
            _.config__save()
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # Health checks
    # ═══════════════════════════════════════════════════════════════════════════

    def health_check__port(self):
        with self.config as _:
            if _.server__process_id:
                if is_port_open(host=_.server__host, port=_.server__port):
                    _.health_check__port__last_status    = True
                    _.health_check__port__last_timestamp = Timestamp_Now()
                    return True

            _.health_check__port__last_status    = False
            _.health_check__port__last_timestamp = None
            return False

    def health_check__service(self):                                                             # override in subclass (API json check, HTTP 200 check, etc)
        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # URL helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def url__for_server(self, path=''):
        with self.config as _:
            base_url = f"{_.server__scheme}://{_.server__host}:{_.server__port}"
            if path and not path.startswith('/'):
                path = f"/{path}"
            return f"{base_url}{path}"

    # ═══════════════════════════════════════════════════════════════════════════
    # Process management
    # ═══════════════════════════════════════════════════════════════════════════

    def server__is_running(self):
        with self.config as _:
            pid = _.server__process_id
            if pid:
                try:
                    os.kill(pid, 0)                                                              # signal 0 just checks if process exists
                    return True
                except OSError:
                    return False
            return False

    def server__configured_ok(self):
        return False

    def server__popen_args(self):                                                                # override in subclass to return the subprocess args
        raise NotImplementedError()

    def server__should_start(self):                                                              # override in subclass for custom restart logic
        with self.config as _:
            return _.server__online is False

    def server__start(self):
        self.config__update()
        with self.config as _:
            if self.server__configured_ok():
                if self.server__should_start():
                    popen_args           = self.server__popen_args()
                    new_process          = subprocess.Popen(popen_args                     ,
                                                            # stderr     = subprocess.PIPE,
                                                            # stdout     = subprocess.PIPE,
                                                            stderr     = subprocess.DEVNULL,            # note: this is needed for the static server, since the binding to localhost or 0.0.0.0 was failing without it
                                                            stdout     = subprocess.DEVNULL,            #       for static hosting (was working ok for FastAPI)
                                                            preexec_fn = os.setsid         )
                    _.server__process_id = new_process.pid
                    _.server__started    = True
                    _.server__stopped    = False

                    if not self.wait_for__port__open():
                        return False

                    if not self.wait_for__server():
                        return False

                    self.config__save()
                    self.config__update()
                    return True
            return False

    def server__stop(self):
        self.config__load()
        with self.config as _:
            if self.server__is_running():
                os.killpg(os.getpgid(_.server__process_id), signal.SIGTERM)             # getpgid to make sure connected processes are also killed
                _.server__stopped = True
                if self.wait_for__port__closed() is False:
                    return False

            _.server__online     = False
            _.server__process_id = None
            _.server__started    = False
            self.config__save()
            self.config__update()
            return _.server__stopped

    # ═══════════════════════════════════════════════════════════════════════════
    # Wait helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def wait_for__port__closed(self):
        with self.config as _:
            return wait_for_port_closed(host=_.server__host, port=_.server__port)

    def wait_for__port__open(self):
        with self.config as _:
            return wait_for_port(host=_.server__host, port=_.server__port)

    def wait_for__server(self):                                                                  # override in subclass for protocol-specific wait
        return True
