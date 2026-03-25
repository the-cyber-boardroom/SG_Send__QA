from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Upload_Page(Type_Safe):                                           # snapshot of the upload wizard's visible state
    state           : str  = ''                                                 # wizard state: idle|file-ready|choosing-delivery|choosing-share|confirming|complete
    file_name       : str  = ''                                                 # selected file name (from wizard header)
    share_link      : str  = ''                                                 # combined link shown in done step
    friendly_token  : str  = ''                                                 # simple token shown in done step
    is_gate_visible : bool = False                                              # access gate input visible?
