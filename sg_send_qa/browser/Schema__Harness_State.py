from osbot_utils.type_safe.Type_Safe import Type_Safe


# [LIB-2026-04-01-013] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
class Schema__Harness_State(Type_Safe):                                         # what gets persisted to disk
    api_port        : int = None                                                # FastAPI server port
    ui_port         : int = None                                                # static file server port
    ui_build_folder : str = None                                                # path to cached built UI files
    ui_version      : str = None                                                # UI version used for build
    ui_content_hash : str = None                                                # md5 hash of UI source files (first 8 chars)
    access_token    : str = None                                                # access token from test server
    chrome_port     : int = None                                                # CDP debug port (mirrors QA_Browser)
