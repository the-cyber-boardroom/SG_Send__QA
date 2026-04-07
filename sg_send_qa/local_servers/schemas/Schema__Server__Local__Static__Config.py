
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now    import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url__Path      import Safe_Str__Url__Path
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Config                 import Schema__Server__Local__Config


# ═══════════════════════════════════════════════════════════════════════════════
# Static HTTP Server Config — adds serve directory and content hash
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Server__Local__Static__Config(Schema__Server__Local__Config):
    health_check__http__path           : Safe_Str__Url__Path     = '/'
    health_check__http__last_status    : bool                    = None
    health_check__http__last_timestamp : Timestamp_Now           = None
    ui__serve_dir                      : str                     = None             # full path to built static files
    ui__content_hash                   : str                     = None             # detect when rebuild + restart needed
