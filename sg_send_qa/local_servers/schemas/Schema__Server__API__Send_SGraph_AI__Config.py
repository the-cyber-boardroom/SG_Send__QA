from osbot_utils.type_safe.primitives.domains.python.safe_str.Safe_Str__Python__Qualified_Name  import Safe_Str__Python__Qualified_Name
from osbot_utils.type_safe.primitives.domains.network.safe_uint.Safe_UInt__Port                 import Safe_UInt__Port
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Fast_API__Config                   import Schema__Server__Local__Fast_API__Config
from sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user                       import run
from tests.qa.local_servers.schemas.safe_str.Safe_Str__Python__FastAPI_Handler import Safe_Str__Python__FastAPI_Handler

# ═══════════════════════════════════════════════════════════════════════════════
# Concrete Config Schemas — project-specific defaults
# ═══════════════════════════════════════════════════════════════════════════════

# @dev can you review the last commit removals since we lost in the factoring some of these static values and started to use hard-coded primitives variables in the codew
SEND_SGRAPH_AI__SERVER__PORT                    = Safe_UInt__Port          (50001)               # @dev: move to common config location # making this fixed since we shouldn't really have many copies of this running at the same time
#SEND_SGRAPH_AI__SERVER__HOST                    = Safe_Str__Url__Host      ('localhost')
#SEND_SGRAPH_AI__SERVER__SCHEME                  = Safe_Id                  ('http')               # @dev: I think an Enum would be better here
SEND_SGRAPH_AI__SERVER__MODULE                  = Safe_Str__Python__Qualified_Name(run.__module__)
#SEND_SGRAPH_AI__FILE_ID__SERVER_CONFIG          = 'api__send-sgraph-ai'
#SEND_SGRAPH_AI__SERVER__API__PATH__HEALTH_CHECK = '/info/status'


class Schema__Server__API__Send_SGraph_AI__Config(Schema__Server__Local__Fast_API__Config):
    fastapi__handler                   : Safe_Str__Python__FastAPI_Handler = f'{SEND_SGRAPH_AI__SERVER__MODULE}:app'
    server__port                       : Safe_UInt__Port                   = SEND_SGRAPH_AI__SERVER__PORT
    server__is_fast_api                : bool                              = True           # kept for backwards compat with existing json
