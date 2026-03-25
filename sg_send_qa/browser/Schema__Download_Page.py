from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Download_Page(Type_Safe):                                         # snapshot of the send-download component state
    state               : str  = ''                                             # component state: loading|entry|ready|decrypting|complete|error
    is_key_input_visible: bool = False                                          # key input visible? (separate key mode, ready state)
    content_text        : str  = ''                                             # decrypted file content (when state=complete)
    error_message       : str  = ''                                             # error description (when state=error)
    transfer_id         : str  = ''                                             # transfer ID from the URL hash
