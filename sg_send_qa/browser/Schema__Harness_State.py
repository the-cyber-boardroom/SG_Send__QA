from osbot_utils.type_safe.Type_Safe import Type_Safe


# todo: refactor all types below to be Type_Safe primitives
class Schema__Harness_State(Type_Safe):                                         # what gets persisted to disk
    api_port        : int = 0                                                   # FastAPI server port
    ui_port         : int = 0                                                   # static file server port
    ui_build_folder : str = ''                                                  # path to cached built UI files
    ui_version      : str = ''                                                  # UI version used for build
    access_token    : str = ''                                                  # access token from test server
    chrome_port     : int = 0                                                   # CDP debug port (mirrors QA_Browser)
