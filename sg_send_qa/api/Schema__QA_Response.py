from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__QA_Response(Type_Safe):                           # base response schema; additional fields added from capture config
    status      : str  = ''                                     # 'pass' | 'fail'
    trace_id    : str  = ''                                     # echoed from request (or auto-generated)
    duration_ms : int  = 0                                      # total request duration in milliseconds
    error       : str  = ''                                     # error message if status == 'fail'
