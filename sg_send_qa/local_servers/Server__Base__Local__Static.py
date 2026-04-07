# ═══════════════════════════════════════════════════════════════════════════════
# Server__Base__Local__Static — Base for static file HTTP subprocess servers
# Launches python -m http.server, validates via HTTP 200 on health check path
# ═══════════════════════════════════════════════════════════════════════════════

import requests

from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now    import Timestamp_Now
from sg_send_qa.local_servers.Server__Base__Local                                   import Server__Base__Local
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Static__Config         import Schema__Server__Local__Static__Config


class Server__Base__Local__Static(Server__Base__Local):                                          # base for static file servers
    config : Schema__Server__Local__Static__Config

    def config_class(self):
        return Schema__Server__Local__Static__Config

    # ═══════════════════════════════════════════════════════════════════════════
    # Health checks
    # ═══════════════════════════════════════════════════════════════════════════

    def health_check__service(self):                                                             # check HTTP 200 on health check path
        return self.health_check__http()

    def health_check__http(self):
        with self.config as _:
            if _.server__port:
                url = self.url__for_server(_.health_check__http__path)
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        _.health_check__http__last_status    = True
                        _.health_check__http__last_timestamp = Timestamp_Now()
                        return True
                except requests.exceptions.ConnectionError:
                    pass

                _.health_check__http__last_status    = False
                _.health_check__http__last_timestamp = None
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # Process management
    # ═══════════════════════════════════════════════════════════════════════════

    def server__needs_restart(self, ui_serve_dir, ui_content_hash):                              # check if running server is stale
        with self.config as _:
            if _.server__online is False:
                return True
            if _.ui__serve_dir != ui_serve_dir:
                return True
            if _.ui__content_hash != ui_content_hash:
                return True
            return False

    def server__configured_ok(self):
        with self.config as _:
            if _.ui__serve_dir and _.server__host and _.server__port:
                return True
            else:
                return False


    def server__popen_args(self):
        with self.config as _:
            return ['python', '-m', 'http.server'   ,
                    '--directory', _.ui__serve_dir   ,
                    '--bind'     , _.server__host,
                    str(_.server__port)              ]

    def server__should_start(self):                                                              # for static servers, always delegate to needs_restart
        with self.config as _:
            return _.server__online is False

    def server__start(self):                                # extended start with content tracking
        with self.config as _:
            if self.server__configured_ok():
                if self.server__needs_restart(_.ui__serve_dir, _.ui__content_hash):                        # todo: see if we need this capability
                    if self.config.server__online:                                                       # stale server — stop first
                        self.config__save()                                                              # save values like the new ui__serve_dir
                        self.server__stop()

                return super().server__start()
        return False

    def wait_for__server(self):
        url = self.url__for_server(self.config.health_check__http__path)
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
