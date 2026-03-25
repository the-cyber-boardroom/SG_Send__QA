from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Viewer_Page(Type_Safe):                                           # snapshot of the single-file viewer
    state           : str  = ''                                                 # component state: loading|entry|ready|decrypting|complete|error
    file_name       : str  = ''                                                 # displayed file name
    content_text    : str  = ''                                                 # visible file content (text files)
    error_message   : str  = ''                                                 # error description (when state=error)
    transfer_id     : str  = ''                                                 # transfer ID from hash fragment
