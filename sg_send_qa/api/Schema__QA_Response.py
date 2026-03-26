from typing                                         import List
from osbot_utils.type_safe.Type_Safe                import Type_Safe
from sg_send_qa.api.Schema__Transition_Observed     import Schema__Transition_Observed


class Schema__QA_Response(Type_Safe):                           # base response schema; additional fields added from capture config
    status               : str                              = '' # 'pass' | 'fail'
    trace_id             : str                              = '' # echoed from request (or auto-generated)
    duration_ms          : int                              = 0  # total request duration in milliseconds
    error                : str                              = '' # error message if status == 'fail'
    transitions_observed : List[Schema__Transition_Observed]    # state transitions recorded during workflow execution
