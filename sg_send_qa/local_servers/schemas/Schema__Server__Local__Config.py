from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                            import Safe_UInt
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                               import Safe_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.network.safe_uint.Safe_UInt__Port                 import Safe_UInt__Port
from sg_send_qa.browser.for__osbot_utils.Safe_Str__Url__Host                                    import Safe_Str__Url__Host

# ═══════════════════════════════════════════════════════════════════════════════
# Base Server Config — shared by all local server types
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Server__Local__Config(Type_Safe):
    health_check__port__last_status    : bool                    = None
    health_check__port__last_timestamp : Timestamp_Now           = None
    server__host                       : Safe_Str__Url__Host     = 'localhost'       # subprocess bind target; static server uses --bind, FastAPI uses --host
    server__online                     : bool                    = False
    server__port                       : Safe_UInt__Port         = None
    server__scheme                     : Safe_Id                 = 'http'
    server__process_id                 : Safe_UInt               = None
    server__started                    : bool                    = False
    server__stopped                    : bool                    = False