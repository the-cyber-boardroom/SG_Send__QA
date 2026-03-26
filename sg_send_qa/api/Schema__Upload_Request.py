from sg_send_qa.api.Schema__QA_Request import Schema__QA_Request


class Schema__Upload_Request(Schema__QA_Request):               # request schema for upload and workflow endpoints
    filename   : str = 'qa-test.txt'                            # filename to use for the uploaded file
    content    : str = ''                                        # base64-encoded file content (empty = default test payload)
    share_mode : str = 'combined'                               # 'combined' | 'token' | 'separate_key'
