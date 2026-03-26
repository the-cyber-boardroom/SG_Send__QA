from osbot_utils.type_safe.Type_Safe              import Type_Safe
from sg_send_qa.api.Schema__Capture_Config        import Schema__Capture_Config


class Schema__QA_Request(Type_Safe):                            # base request schema for all QA API endpoints
    target       : str                    = 'local'             # 'local' or live URL e.g. 'https://send.sgraph.ai'
    access_token : str                    = ''                  # SG/Send access token (caller-provided; discarded after request)
    mode         : str                    = 'smoke'             # 'smoke' (minimal capture) or 'qa' (full capture)
    trace_id     : str                    = ''                  # auto-generated if not provided; propagated to browser headers
    capture      : Schema__Capture_Config = None                # None → defaults populated by runner based on mode
    options      : dict                   = None                # endpoint-specific extra parameters
