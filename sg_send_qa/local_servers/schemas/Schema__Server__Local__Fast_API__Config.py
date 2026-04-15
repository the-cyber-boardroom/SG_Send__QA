from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url__Path                  import Safe_Str__Url__Path
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Config                             import Schema__Server__Local__Config
from sg_send_qa.local_servers.schemas.safe_str.Safe_Str__Python__FastAPI_Handler import Safe_Str__Python__FastAPI_Handler


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Server Config — adds handler ref and API health check
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Server__Local__Fast_API__Config(Schema__Server__Local__Config):
    fastapi__handler                   : Safe_Str__Python__FastAPI_Handler   = None
    health_check__api__path            : Safe_Str__Url__Path                 = '/info/status'
    health_check__api__last_status     : bool                                = None
    health_check__api__last_response   : dict                                = None
    health_check__api__last_timestamp  : Timestamp_Now                       = None
