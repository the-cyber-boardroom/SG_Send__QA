# ═══════════════════════════════════════════════════════════════════════════════
# Server__Base__Local__Fast_API — Base for FastAPI subprocess servers
# Adds uvicorn launch args and JSON health check endpoint validation
# ═══════════════════════════════════════════════════════════════════════════════

import requests

from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now    import Timestamp_Now
from osbot_utils.utils.Http                                                         import url_join_safe, wait_for_http
from sg_send_qa.local_servers.Server__Base__Local                                   import Server__Base__Local
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Fast_API__Config       import Schema__Server__Local__Fast_API__Config


class Server__Base__Local__Fast_API(Server__Base__Local):                                        # base for FastAPI servers launched via uvicorn
    config : Schema__Server__Local__Fast_API__Config

    def config_class(self):
        return Schema__Server__Local__Fast_API__Config

    # ═══════════════════════════════════════════════════════════════════════════
    # Health checks
    # ═══════════════════════════════════════════════════════════════════════════

    def health_check__service(self):                                                             # check the API health endpoint returns 200 + JSON
        return self.health_check__api()

    def health_check__api(self):
        with self.config as _:
            if _.server__port:
                url = self.url__for_health_check()
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

    # ═══════════════════════════════════════════════════════════════════════════
    # URL helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def url__for_health_check(self):
        with self.config as _:
            base_path = f"{_.server__scheme}://{_.server__host}:{_.server__port}"
            return url_join_safe(base_path, _.health_check__api__path)

    # ═══════════════════════════════════════════════════════════════════════════
    # Process management
    # ═══════════════════════════════════════════════════════════════════════════

    def server__configured_ok(self):
        return True                             # todo: @dev add checks to make sure all vars valued to safely create the process are correctly set up (see how the __Static was implemented)

    def server__popen_args(self):
        import sys
        with self.config as _:
            return [sys.executable, '-m', 'uvicorn'             ,   # use same Python that's running the tests
                    _.fastapi__handler                          ,
                    '--host'                    , _.server__host     ,
                    '--port'                    , str(_.server__port),
                    '--log-level'               , 'info'            ,
                    '--timeout-graceful-shutdown', '0'               ]

    def wait_for__server(self):
        url = self.url__for_health_check()
        return wait_for_http(url)
