# ═══════════════════════════════════════════════════════════════════════════════
# Server__Http__Send_SGraph_AI — SG/Send static UI server on port 50002
# Thin subclass: just wires the config schema and server id
# ═══════════════════════════════════════════════════════════════════════════════

from sg_send_qa.local_servers.Server__Base__Local__Static                          import Server__Base__Local__Static
from sg_send_qa.local_servers.schemas.Schema__Server__Http__Send_SGraph_AI__Config import Schema__Server__Http__Send_SGraph_AI__Config

SEND_SGRAPH_AI__FILE_ID__HTTP_SERVER_CONFIG = 'http__send-sgraph-ai'

class Server__Http__Send_SGraph_AI(Server__Base__Local__Static):                                 # SG/Send static UI server lifecycle
    config    : Schema__Server__Http__Send_SGraph_AI__Config
    server_id : str = SEND_SGRAPH_AI__FILE_ID__HTTP_SERVER_CONFIG                                # @dev use Safe_Id once default value auto-conversion is confirmed

    def config_class(self):
        return Schema__Server__Http__Send_SGraph_AI__Config
