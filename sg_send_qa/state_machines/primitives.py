"""Domain-specific Safe_Str types for state machine definitions.

One-line subclasses of Safe_Str__Id.  Safe_Str__Id allows alphanumerics
plus '-' and '_', max 128 chars — fits all SG/Send state and trigger names.
"""
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class Safe_Str__State_Name   (Safe_Str__Id): pass   # e.g. 'idle', 'confirming', 'complete'
class Safe_Str__Trigger_Name (Safe_Str__Id): pass   # e.g. 'file_selected', 'click_next'
class Safe_Str__Guard_Expr   (Safe_Str__Id): pass   # e.g. 'file_input_has_file'
class Safe_Str__Security_Tag (Safe_Str__Id): pass   # e.g. 'plaintext_in_memory', 'key_in_url'
class Safe_Str__Machine_Name (Safe_Str__Id): pass   # e.g. 'upload_wizard', 'download_flow'
