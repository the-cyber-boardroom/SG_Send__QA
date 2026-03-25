from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Gallery_Page(Type_Safe):                                          # snapshot of the gallery view (multi-file transfer)
    state           : str  = ''                                                 # component state: loading|entry|ready|decrypting|complete|error
    file_count      : int  = 0                                                  # number of files listed in the gallery
    content_text    : str  = ''                                                 # visible text content on the gallery page
    error_message   : str  = ''                                                 # error description (when state=error)
    transfer_id     : str  = ''                                                 # transfer ID from hash fragment
