from osbot_utils.type_safe.Type_Safe                         import Type_Safe
from sg_send_qa.browser.for__osbot_utils.Safe_Str__Url__Host import Safe_Str__Url__Host


class Schema__Browser_Test_Config(Type_Safe):                                   # configuration for a browser test session
    headless        : bool                 = True                                               # True for CI, False for local debugging
    capture_stderr  : bool                 = True                                               # suppress Chrome/server noise in test output
    host            : Safe_Str__Url__Host  = 'localhost'                                         # must be 'localhost' for Web Crypto secure context

