# ═══════════════════════════════════════════════════════════════════════════════
# Safe_Str__Python__FastAPI_Handler — e.g. 'my_app.module:app'
# Extends qualified name to allow the colon separator used by uvicorn
# ═══════════════════════════════════════════════════════════════════════════════

# todo move to OSBot_Fast_API project
import re
from osbot_utils.type_safe.primitives.core.Safe_Str                                             import Safe_Str


class Safe_Str__Python__FastAPI_Handler(Safe_Str):                                               # module.path:variable format
    max_length = 512
    regex      = re.compile(r'[^a-zA-Z0-9_.:]')                                                 # allows dots and colon
