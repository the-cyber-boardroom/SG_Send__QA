# ═══════════════════════════════════════════════════════════════════════════════
# Server__API__Send_SGraph_AI — SG/Send FastAPI server on port 50001
# Thin subclass: just wires the config schema and server id
# ═══════════════════════════════════════════════════════════════════════════════

from sg_send_qa.local_servers.Server__Base__Local__Fast_API                       import Server__Base__Local__Fast_API
from sg_send_qa.local_servers.schemas.Schema__Server__API__Send_SGraph_AI__Config import Schema__Server__API__Send_SGraph_AI__Config

SEND_SGRAPH_AI__FILE_ID__API_SERVER_CONFIG = 'api__send-sgraph-ai'

class Server__API__Send_SGraph_AI(Server__Base__Local__Fast_API):                                # SG/Send API server lifecycle
    config    : Schema__Server__API__Send_SGraph_AI__Config
    server_id : str = SEND_SGRAPH_AI__FILE_ID__API_SERVER_CONFIG                                 # @dev use Safe_Id once default value auto-conversion is confirmed

    def config_class(self):
        return Schema__Server__API__Send_SGraph_AI__Config
