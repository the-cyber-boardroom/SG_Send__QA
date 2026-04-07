from osbot_utils.type_safe.primitives.domains.network.safe_uint.Safe_UInt__Port                 import Safe_UInt__Port
from sg_send_qa.local_servers.schemas.Schema__Server__Local__Static__Config                     import Schema__Server__Local__Static__Config


# ═══════════════════════════════════════════════════════════════════════════════
# Concrete Config Schemas — project-specific defaults
# ═══════════════════════════════════════════════════════════════════════════════
class Schema__Server__Http__Send_SGraph_AI__Config(Schema__Server__Local__Static__Config):
    server__port                       : Safe_UInt__Port         = 50002
