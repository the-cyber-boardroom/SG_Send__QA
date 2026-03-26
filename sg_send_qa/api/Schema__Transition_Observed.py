from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Transition_Observed(Type_Safe):
    """A single UI state transition recorded during workflow execution."""
    from_state : str = ''
    to_state   : str = ''
    trigger    : str = ''
