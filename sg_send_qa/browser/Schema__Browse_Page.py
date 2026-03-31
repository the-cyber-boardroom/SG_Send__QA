from osbot_utils.type_safe.Type_Safe import Type_Safe

# todo refactor to schema folder and to Type_Safe primitives
#      state should be an Enum (and should be connected to the state machine)
class Schema__Browse_Page(Type_Safe):                                           # snapshot of the browse/combined-link view
    state           : str  = ''                                                 # download component state: loading|entry|ready|decrypting|complete|error
    content_text    : str  = ''                                                 # decrypted content visible on page (when state=complete)
    error_message   : str  = ''                                                 # error description (when state=error)
    transfer_id     : str  = ''                                                 # transfer ID from hash fragment
    friendly_token  : str  = ''                                                 # friendly token from hash (word-word-NNNN), if used
