# [LIB-2026-04-01-042] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
import pytest
import requests
from unittest                                                                    import TestCase
from osbot_fast_api.utils.Fast_API_Server                                         import Fast_API_Server
from playwright.sync_api import PlaywrightContextManager

from osbot_utils.helpers.duration.decorators.capture_duration                     import capture_duration
from osbot_utils.helpers.duration.decorators.print_duration                       import print_duration
from osbot_utils.testing.__                                                       import __, __SKIP__, __BETWEEN__
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.utils.Http                                                       import is_port_open, wait_for_port_closed
from osbot_utils.utils.Objects                                                    import base_types
from osbot_utils.utils.Process                                                    import kill_process
from sg_send_qa.apis_for_sites.send_sgraph_ai.pages.Page__Send_SGraph_Ai__Upload  import Page__Send_SGraph_Ai__Upload
from sg_send_qa.browser.SG_Send__Browser__Pages                                   import SG_Send__Browser__Pages
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                            import SG_Send__Browser__Test_Harness
from sg_send_qa.browser.Schema__Browser_Test_Config                               import Schema__Browser_Test_Config
from sg_send_qa.browser.for__osbot_playwright.SG_Send__Playwright_Browser__Chrome import SG_Send__Playwright_Browser__Chrome


# @qa we don't need this class (see comment on next class
# # ═══════════════════════════════════════════════════════════════════════════════
# # Non-browser unit tests — run in CI without Chromium
# # ═══════════════════════════════════════════════════════════════════════════════

# # @qa we should not be using docstrings for class comments, they should go at the end of the function line, aligned with the other comments
# #      just like below
# class test_Page__Send_SGraph_Ai__Upload__Unit(TestCase):                        # Unit tests for Page__Send_SGraph_Ai__Upload — no browser required.
#
#     # @qa I think test__init__ is a better name for what this test is doing
#     #def test_instantiation(self):                                               # class can be constructed with no arguments
#     def test__init__(self):                                                     # check class default values
#         # @qa for classes that implement type safe, instead of doing this which doesn't gives us a lot
#         #   page = Page__Send_SGraph_Ai__Upload()
#         #   assert page is not None
#         # using this technique we confirm a lot of more things while also providing a visual view of the objects we are working with
#         with Page__Send_SGraph_Ai__Upload() as _:                                       # @qa create the object and assign to _ (which makes the code easier to read)
#             assert type(_)          is Page__Send_SGraph_Ai__Upload                     #     simple way to confirm that all worked well
#             assert base_types(_)    == [Type_Safe, object]                              #     good way to confirm that this is a Type_Safe class
#             assert _.obj()          == __(harness = None,                               #     .obj() is a sophisticated way to check the default values
#                                           sg_send = None,                               #          due to special attributes like __SKIP__ which handle ok non-deterministic values
#                                           config  = __(headless       = True       ,
#                                                        capture_stderr = True       ,
#                                                        host           ='localhost'))    # @qa note the formating and alignment of this method
#             assert _.teardown() is False                                                # @qa this is also a nice place to put this simple confirmation
#
#         # @qa the other problem I can see here is why are we creating a new instance of Page__Send_SGraph_Ai__Upload for every test method in this class
#
#     # @qa we don't need to test this here
#     # def test_is_type_safe_subclass(self):                                     # must be a Type_Safe subclass (project convention)
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     assert isinstance(page, Type_Safe)
#
#     # @qa this is also already tests
#     # def test_config_defaults_to_headless_true(self):                         # CI safety: headless must default to True
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     assert isinstance(page.config, Schema__Browser_Test_Config)
#     #     assert page.config.headless is True
#
#     def test_config_can_be_overridden_to_headless_false(self):                  # debug path: caller can force visible browser
#         config = Schema__Browser_Test_Config(headless=False)
#         with Page__Send_SGraph_Ai__Upload(config=config) as _:                  # @qa this pattern makes it easier to read
#             assert _.config.headless is False
#
#     # @qa these two are also tested by __init__
#     # def test_harness_is_none_before_setup(self):                             # harness must not be started until setup() is called
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     assert page.harness is None
#     #
#     # def test_sg_send_is_none_before_setup(self):                             # sg_send (browser pages) must not exist until setup()
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     assert page.sg_send is None
#
#     # @qa these methods are redundant since we will be testing this by the tests below that use these methods: setup, upload_file, get_friendly_token, teardown
#     # def test_has_setup_method(self):                                         # setup() must be present and callable
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     assert callable(getattr(page, 'setup', None))
#     #
#     # def test_has_upload_file_method(self):                                   # upload_file() must be present and callable
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     assert callable(getattr(page, 'upload_file', None))
#     #
#     # def test_has_get_friendly_token_method(self):                            # get_friendly_token() must be present and callable
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     assert callable(getattr(page, 'get_friendly_token', None))
#     #
#     # def test_has_teardown_method(self):                                      # teardown() must be present and callable
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     assert callable(getattr(page, 'teardown', None))
#
#     # @qa this is a good example of a test that we need to make more deterministic
#     #     the problem here is that we don't get any clues from .teardown() about what happened (since teardown at the moment returns false
#     #     to improve this I will change next return logic of .teardown()
#     # def test_teardown_is_safe_when_harness_is_none(self):                    # teardown() must not raise if setup() was never called
#     #     page = Page__Send_SGraph_Ai__Upload()
#     #     page.teardown()                                                       # should complete without error
#     # @qa (note after refactoring), since there wasn't really much happening here,
#     #                               after adding the return {bool} to the .teardown() method
#     #                               I added the assert to test__init__




class test_Page__Send_SGraph_Ai__Upload(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upload_page = Page__Send_SGraph_Ai__Upload()

    # @classmethod
    # def tearDownClass(cls):
    #     cls.upload_page.harness.teardown()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Non-browser unit tests — run in CI without Chromium
    # ═══════════════════════════════════════════════════════════════════════════════

    # @qa these two are refactored from test_Page__Send_SGraph_Ai__Upload__Unit (above)
    def test__init__(self):                                                             # check class default values
        with Page__Send_SGraph_Ai__Upload() as _:
            assert type(_)          is Page__Send_SGraph_Ai__Upload                     # @qa, can you add some comments to these lines?
            assert base_types(_)    == [Type_Safe, object]
            assert _.obj()          == __(harness = None,
                                          sg_send = None,
                                          config  = __(headless       = True       ,
                                                       capture_stderr = True       ,
                                                       host           ='localhost'))
            assert _.teardown() is False

    def test_config_can_be_overridden_to_headless_false(self):                  # debug path: caller can force visible browser
        config = Schema__Browser_Test_Config(headless=False)
        with Page__Send_SGraph_Ai__Upload(config=config) as _:
            assert _.config.headless is False


    # ═══════════════════════════════════════════════════════════════════════════════
    # Browser tests — require Chromium
    # ═══════════════════════════════════════════════════════════════════════════════
    # @qa all these tests should always run with a live browser (since that is the point of them), what we want to do is to make the process of starting and reusing the browser as effective as possible
    #@pytest.mark.skip("requires browser — run manually")
    # def test_setup_and_teardown_headless(self):                                 # verify headless setup/teardown lifecycle
    #     with Page__Send_SGraph_Ai__Upload() as _:                               # @qa as this stands this is a test that doesn't really check for much
    #         _.setup()                                                           #       since this is perfect place to really make sure that all our assumption are correct
    #         assert _.harness   is not None                                      #       and as long as there aren't performance implications, or we are adding a lot of complexity
    #         assert _.sg_send   is not None                                      #       this is also a great place to provide a more visual explanation of what just happened with the setup
    #         assert _.config.headless is True                                    #       and what are the state of the objects
    #         _.teardown()                                                        #       next, I'm going to comment out this test and recreate it

    def test_setup_and_teardown_headless(self):

        with Page__Send_SGraph_Ai__Upload() as _:
            with capture_duration() as duration__setup:
                assert type(_.setup())   is Page__Send_SGraph_Ai__Upload         # @qa this is a much better way to test, since we confirm the exact types
                assert type(_.harness)   is SG_Send__Browser__Test_Harness
                assert type(_.sg_send)   is SG_Send__Browser__Pages              # @qa note how the sg_send is not a good one to use here
                assert _.config.headless is True
                # @qa the problem with the test above is that we are not really testing what is the state of Page__Send_SGraph_Ai__Upload object
                #assert _.obj() == __()                                          # @qa ideally this is how we would do it
                #                                                                #     but we are getting a recursion error:
                                                                                 #          E   RecursionError: maximum recursion depth exceeded
                                                                                 #          !!! Recursion detected (same locals & position)
                                                                                 #     .... so let's see where
                assert _.config.obj() == __(headless       = True       ,        # @qa this is ok, and also a much better way to confirm the value of config.headless
                                            capture_stderr = True       ,
                                            host           = 'localhost')

                #assert _.harness.obj() == __()                                 # @qa ok here is where we have the recursive loop
                                                                                #     note that I use the trick "{Type_Safe()}.obj() == __()" since the assert error provides the values that should be here (i.e. a nice way to get the correct values)
                assert _.sg_send.obj() == __(headless      = True                   ,   # @qa works ok, and we confirm the values assigned
                                             target_port   = __BETWEEN__(1000,65000),   #     __BETWEEN__ is one of the techniques used with the class __() to (in this case) confirm that the port is an int between these two values
                                             target_server ='http://localhost'      )
                # @qa next lets see what is happening with _.harness.obj()
                assert _.harness.config       .obj()      == __(headless=True, capture_stderr=True, host='localhost')
                assert _.harness.persistence  .obj() == __()
                #assert _.harness.api_server  .obj() == __()      # recursion error
                #assert _.harness.ui_folder   .obj() == __()     # not a Type_Safe class        # @dev fix in OSBot_Utils
                #assert _.harness.ui_server   .obj() == __()     # not a Type_Safe class        # @dev fix in OSBot_Utils
                #assert _.harness.stderr      .obj() == __()     # not a Type_Safe class
                assert _.harness.sg_send      .obj() == __(headless=True, target_port=__SKIP__, target_server='http://localhost')
                # @qa new subprocess architecture: test_objs and api_server are None
                # test_objs was used in the old in-process FastAPI architecture (setup__send_user_lambda__test_client)
                # In the subprocess arch the server is an external process — test_objs is never populated
                assert _.harness.test_objs   is None                               # subprocess arch: no in-process test client
                assert _.harness.api_server  is None                               # subprocess arch: api_server replaced by server__send_graph_ai__api
                # The new subprocess servers are the live objects to assert against
                from sg_send_qa.local_servers.Server__API__Send_SGraph_AI  import Server__API__Send_SGraph_AI
                from sg_send_qa.local_servers.Server__Http__Send_SGraph_AI import Server__Http__Send_SGraph_AI
                assert type(_.harness.server__send_graph_ai__api ) is Server__API__Send_SGraph_AI
                assert type(_.harness.server__send_graph_ai__http) is Server__Http__Send_SGraph_AI
                # with _.harness.api_server as fast_api_server:                # let's move to a more relevant context
                #     assert fast_api_server.obj() == __(app       = __SKIP__,
                #                                        port      = __SKIP__,
                #                                        log_level = __SKIP__,
                #                                        config    = __SKIP__,
                #                                        server    = __SKIP__,
                #                                        thread    = __SKIP__,
                #                                        running   = __SKIP__,
                #                                        stdout    = __SKIP__,
                #                                        stderr    = __SKIP__)

                # @qa ok, I was not able to figure what is causing the recursive error, but I think it is due to some circular dependencies that exist in the code
                #         which we need to figure out where (this is where it is worth writing a set of tests just to focus on this
                #         note that Fast_API_Server.obj() works ok (as seen below)
                assert Fast_API_Server().obj() == __(log_level='error',
                                                       config=__(app='FastAPI',
                                                                 host='127.0.0.1',
                                                                 port=__SKIP__,
                                                                 uds=None,
                                                                 fd=None,
                                                                 loop='auto',
                                                                 http='auto',
                                                                 ws='auto',
                                                                 ws_max_size=16777216,
                                                                 ws_max_queue=32,
                                                                 ws_ping_interval=20.0,
                                                                 ws_ping_timeout=20.0,
                                                                 ws_per_message_deflate=True,
                                                                 lifespan='auto',
                                                                 log_config=__(version=1,
                                                                               disable_existing_loggers=False,
                                                                               formatters=__(default=__(__='uvicorn.logging.DefaultFormatter',
                                                                                                        fmt='%(levelprefix)s '
                                                                                                            '%(message)s',
                                                                                                        use_colors=None),
                                                                                             access=__(__='uvicorn.logging.AccessFormatter',
                                                                                                       fmt='%(levelprefix)s '
                                                                                                           '%(client_addr)s - '
                                                                                                           '"%(request_line)s" '
                                                                                                           '%(status_code)s')),
                                                                               handlers=__(default=__(formatter='default',
                                                                                                      _class='logging.StreamHandler',
                                                                                                      stream='ext://sys.stderr'),
                                                                                           access=__(formatter='access',
                                                                                                     _class='logging.StreamHandler',
                                                                                                     stream='ext://sys.stdout')),
                                                                               loggers=__(uvicorn=__(handlers=['default'],
                                                                                                     level='INFO',
                                                                                                     propagate=False),
                                                                                          uvicorn_error=__(level='INFO'),
                                                                                          uvicorn_access=__(handlers=['access'],
                                                                                                            level='INFO',
                                                                                                            propagate=False))),
                                                                 log_level='error',
                                                                 access_log=True,
                                                                 use_colors=None,
                                                                 interface='auto',
                                                                 reload=False,
                                                                 reload_delay=0.25,
                                                                 workers=1,
                                                                 proxy_headers=True,
                                                                 server_header=True,
                                                                 date_header=True,
                                                                 root_path='',
                                                                 limit_concurrency=None,
                                                                 limit_max_requests=None,
                                                                 limit_max_requests_jitter=0,
                                                                 backlog=2048,
                                                                 timeout_keep_alive=5,
                                                                 timeout_notify=30,
                                                                 timeout_graceful_shutdown=None,
                                                                 timeout_worker_healthcheck=5,
                                                                 callback_notify=None,
                                                                 ssl_keyfile=None,
                                                                 ssl_certfile=None,
                                                                 ssl_keyfile_password=None,
                                                                 ssl_version=17,
                                                                 ssl_cert_reqs=0,
                                                                 ssl_ca_certs=None,
                                                                 ssl_ciphers='TLSv1',
                                                                 headers=[],
                                                                 encoded_headers=[],
                                                                 factory=False,
                                                                 h11_max_incomplete_event_size=None,
                                                                 loaded=False,
                                                                 reload_dirs=[],
                                                                 reload_dirs_excludes=[],
                                                                 reload_includes=[],
                                                                 reload_excludes=[],
                                                                 forwarded_allow_ips='127.0.0.1'),
                                                       server=None,
                                                       thread=None,
                                                       running=False,
                                                       app='FastAPI',
                                                       port=__SKIP__,
                                                       stdout=__(output=__(),
                                                                 redirect_stdout=__(_new_target=__(), _old_targets=[])),
                                                       stderr=__(output=__(), redirect_stderr=__(_new_target=__(), _old_targets=[])))

            # 'Fast_API__SGraph__App__Send__User'
            with capture_duration() as duration__teardown:
                _.teardown()

            assert duration__setup.seconds      < 2                                     # note: on my osx laptop , on battery
            assert duration__teardown.seconds   < 0.5


            # assert duration__teardown           < 0.5                                 # @dev add support for this pattern to OSBot_Utils

            # @qa at the moment when we execute this test we get the console message (which should had been captured)
            #     DevTools listening on ws://127.0.0.1:26945/devtools/browser/8cdf1bb7-6fe3-4ed3-aedc-d98a88de8134

    def test_setup_and_teardown_headless__false__using_singleton__qa_browser(self):
        with Page__Send_SGraph_Ai__Upload() as _:                               # first object
            with print_duration(action_name = "setup and execution"):           # ~ 0.031 seconds

                assert _.headless(False)  is _
                assert _.setup   ()       is _

            with print_duration(action_name = "invoke qa_browser singleton"):   # ~ 0.571 seconds
                _.sg_send.qa_browser()

            with print_duration(action_name = "open page"):
                _.sg_send.open('404', wait_for_ready=False)                     # 0.061 seconds

        # @qa so above we confirm that _.sg_send.qa_browser() is the one we want to capture

        # now all this work without errors (note that at the moment we can't mix headless and non-headless modes , or we get back our async error)
        with Page__Send_SGraph_Ai__Upload() as _:
            _.headless(False)
            _.setup   ()

            _.sg_send.qa_browser()

        with SG_Send__Browser__Pages() as _:
            _.headless = False
            _.qa_browser()

        # @qa and running these again, now gives use the performance we want

        with Page__Send_SGraph_Ai__Upload() as _:                               # first object
            with print_duration(action_name = "setup and execution"):           # ~ 0.036 seconds

                assert _.headless(False)  is _
                assert _.setup   ()       is _

            with print_duration(action_name = "invoke qa_browser singleton"):   # ~ 0.0 seconds
                _.sg_send.qa_browser()

            with print_duration(action_name = "open 404 page"):
                _.sg_send.open('404', wait_for_ready=False)                     # ~ 0.054 seconds

            with print_duration(action_name = "open root page"):
                _.sg_send.open('', wait_for_ready=True)                         # ~ 0.084 seconds

        # @qa i.e. ~36ms to setup, ~54ms to the 404 page and ~84ms to the main root page


    # @qa ok now lets look at the impact of _start_ui_server (and see if we need to also keep it alive)
    def test_setup_and_teardown_headless__false(self):
        with Page__Send_SGraph_Ai__Upload() as _:
            with print_duration(action_name = "setup and execution"):

                assert _.headless(False)  is _
                assert _.setup   ()       is _


                # @qa let's continue here the discovery of why it takes ~850ms to open the first page (i.e. connect the browser)
                #     since there are no process to start (Chromium is already up) this should be faster
                url = _.sg_send.url__for_path(path='404')
                with print_duration(action_name = "first call"):              # 404 page
                    # _.sg_send.open('404', wait_for_ready=False)             # ~ 0.933 seconds
                    # _.sg_send.raw_page().goto(url)                          # ~ 0.979 seconds
                    # _.sg_send.raw_page()                                    # ~ 0.751 seconds
                    # _.sg_send.page()                                        # ~ 0.773 seconds
                    # _.sg_send.page().page                                   # ~ 0.774 seconds
                    # _.sg_send.qa_browser()                                  # ~ 0     seconds
                    # _.sg_send.qa_browser().chrome()                         # ~ 0.385 seconds
                    # _.sg_send.qa_browser().chrome().page()                  # ~ 0.752 seconds
                    # chromium_executable_path()                              # ~ 0.236 seconds
                    # SG_Send__Playwright_Browser__Chrome()                   # ~ 0.267 seconds

                    # (all stats above where before refactoring of chromium_executable_path), the ones below are after
                    # SG_Send__Playwright_Browser__Chrome()                                 # ~ 0.004 seconds
                    # _.sg_send.qa_browser().chrome()                                       # ~ 0.006 seconds
                    # _.sg_send.qa_browser().chrome().page()                                # ~ 0.577 seconds
                    #_.sg_send.qa_browser().chrome().browser()                              # ~ 0.593 seconds
                    #_.sg_send.qa_browser().chrome().playwright()                           # ~ 0.225 seconds
                    # _.sg_send.qa_browser().chrome().playwright_context_manager()          # ~ 0.005 seconds
                    #_.sg_send.qa_browser().chrome().playwright_context_manager().start()    # ~ 0.211 seconds
                    # PlaywrightContextManager().start()                                      # ~ 0.225 seconds
                    # @qa so there is not much we can do here since this is inside the Playwright code base

                    # @dev if we call this twice, we get the error "playwright._impl._errors.Error: It looks like you are using Playwright Sync API inside the asyncio loop."
                    #           PlaywrightContextManager().start()
                    #           PlaywrightContextManager().start()
                    #       which is a good clue for the case where we want to be able to keep a copy of this context over multiple test classes executions (so that we only pay the cost of this connection once)
                    #       this connection to a running chrome is something we should add to a singleton that we need to create with the revised test_objs class and setup

                    # now back to
                    _.sg_send.qa_browser().chrome().playwright()                           # ~ 0.225 seconds

                with print_duration(action_name = "second call"):
                    #_.sg_send.qa_browser().chrome().playwright()                           # ~ 0.0 seconds (it is cached)
                    _.sg_send.qa_browser().chrome().browser()                               # ~ 0.395 seconds (with  0.392 seconds comming from Playwright_Browser.browser_via_cdp)

                with print_duration(action_name = "third call"):
                    #_.sg_send.qa_browser().chrome().browser()                               # ~ 0.0 seconds
                    _.sg_send.qa_browser().chrome().pages()                                 # ~ 0.0 seconds
                    _.sg_send.qa_browser().chrome().page ()                                 # ~ 0.0 seconds

                    #_.sg_send.qa_browser().open(url)                                        # ~ 0.095 seconds
                    #_.sg_send.open('/404', wait_for_ready=False)                            # ~ 0.091 seconds
                    #_.sg_send.open('', wait_for_ready=False)                               # ~ 0.088 seconds
                    _.sg_send.open('', wait_for_ready=True)                                # ~ 0.124 seconds



                    # @qa ok, so from the data above we can see that the main overhead that we have is
                    #           a) the playwright sync object creation
                    #           b) the browser_via_cdp action
                    #     after that we are having ~90ms to load a 404 and ~150ms to load the full UI (which has quite a good number of imports)


                    # @qa ok from the test above we can see that chromium_executable_path() is one of the bottlenecks
                    # here is its code
                    #               def chromium_executable_path():                                                         # resolve Chromium binary from playwright's own registry
                    #                   with print_duration(action_name="load sync_playwright dependencies"):               # ~ 0.0 seconds
                    #                       from playwright.sync_api import sync_playwright                                 # late import — avoids circular deps
                    #                   with print_duration(action_name="chromium_executable_path -sync_playwright start"): # ~ 0.374 seconds
                    #                       pw   = sync_playwright().start()
                    #                       path = pw.chromium.executable_path
                    #                   with print_duration(action_name="chromium_executable_path -sync_playwright stop"):  # ~ 0.004 seconds
                    #                       pw.stop()
                    #                       return path
                    #
                    # which is for every time we create an SG_Send__Playwright_Browser__Chrome object
                    #   starting and stoping a full sync_playwright process
                    #   just to calculate something that is doesn't change very often (the executable path of the local chromium)
                    #   so the solution is to cache this value and make sure it is only called once



                # with print_duration(action_name = "2nd call"):
                #     _.sg_send.qa_browser().chrome().page()                   # ~ 549   seconds

                return




            # @qa the self.create_browser() in SG_Send__Browser__Test_Harness.setup() did not add any duration (which makes sense since that just created the object),
            #     but opening up a page takes about 800ms, let's do that in parts here

                with print_duration(action_name = "open qa page (1st)"):    # open QA page (first time)
                    _.sg_send.page__qa_setup()                              # ~ 0.933 seconds

                with print_duration(action_name = "open 404 page"):         # open a 404 page
                    _.sg_send.open("404", wait_for_ready=False)             # ~ 0.053 seconds

                with print_duration(action_name = "open qa page (2nd)"):    # open QA page (second time)
                    _.sg_send.page__qa_setup()                              # ~ 0.043 seconds

                with print_duration(action_name = "open root page (1st)"):  # open root '/' (first time)
                    _.sg_send.page__root()                                  # ~ 0.105 seconds

                with print_duration(action_name = "open qa page (3rd)"):    # open QA page (third time)
                    _.sg_send.page__qa_setup()                              # ~ 0.044 seconds

                with print_duration(action_name = "open root page (2nd)"):  # open root '/' (second time)
                    _.sg_send.page__root()                                  # ~ 0.095 seconds

                # qa: analysis of the data above, ok so we can see from the above data that there is about an
                #     ~850ms overhead on the first call, which we need to figure out what is causing it

            # note that the code above is nicely reusing the pre-existent chromium and SG/Send API+UI processes

            # @qa ok, so with the latest changes we now have all this flow running in ~31m in SG_Send__Browser__Test_Harness
            #
            #           def setup(self):
            #                   saved_state = self._load_saved_state()
            #                   self.start_api_server(saved_state)
            #                   self.build_ui        (saved_state)
            #                   self.start_ui_server(saved_state)
            #                   self._save_state()

            # @qa ok so with "self.build_ui(saved_state)"  on SG_Send__Browser__Test_Harness.setup()
            #       on first run we had ~ 0.792 seconds
            #       on next runs we had ~: 0.09 seconds     # but looking at the code we are still calling build_ui_serve_dir

            # @qa and @dev update on the above and on the comments I just added to the codebase
            #      after using the version value for detecting changes to the UI code
            #      build_ui() now uses the cached folder, and the .setup() method takes ~ 0.012 seconds (which is more like it)
            #      for reference the setup code is current doing (with a couple steps missing, but getting there):

            #           saved_state = self._load_saved_state()
            #           self.start_api_server(saved_state)
            #           self.build_ui        (saved_state)
            #           self._save_state()



            # @qa these are the checks that I added during the refactoring of the .start_api_server()
            server_port  = _.harness.server__send_graph_ai__api.config.server__port
            assert is_port_open('localhost', server_port) is True

            assert _.harness.server__send_graph_ai__api.config.obj() == __(fastapi__handler='sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user:app',
                                                                           health_check__api__path='/info/status',
                                                                           health_check__api__last_status=True,
                                                                           health_check__api__last_timestamp=__SKIP__,
                                                                           health_check__api__last_response=__(name='osbot_fast_api_serverless',
                                                                                                               version=__SKIP__,
                                                                                                               status='operational',
                                                                                                               environment='local'),
                                                                           health_check__port__last_status=True,
                                                                           health_check__port__last_timestamp=__SKIP__,
                                                                           server__host='localhost',
                                                                           server__is_fast_api=True,
                                                                           server__online=True,
                                                                           server__port=50001,
                                                                           server__scheme='http',
                                                                           server__process_id=__SKIP__,
                                                                           server__started=True,
                                                                           server__stopped=False)

            # @qa ok so now first time the code executes we get
            #           action took: 1.504 seconds
            #     next execution is :
            #           action took: 0.015 seconds
            #     :) which is exactly what we want , with the full SG/Send server staying alive over executions at http://localhost:50001/info/status
            #     with the config data stored here: modules/SG_Send__QA/.local-servers/server-configs/api__send-sgraph-ai.json



                #assert _.teardown() is True
                # qa: ok as it stands the code above takes ~ 0.905 seconds
                #     without the .harness.set_access_token() and sg_send.page__root() it is still taking about 200ms
                #     running with code coverage I can see that inside harness.setup()
                #        in _start_api_server, we are still trying to start api server
                #        even though it exists
                #        so the prob is that self.api_server_port_open(api_port) returns False
                #        found one bug, the signature of port_is_open is : def port_is_open(port : int , host='0.0.0.0', timeout=1.0):
                #          #  return port_is_open('localhost', port) # bug
                #           return port_is_open(host='localhost', port=port)


    @pytest.mark.skip("requires browser — run manually")
    def test_upload_file_returns_friendly_token(self, tmp_path):             # upload a temp file and get back a word-word-NNNN token
        import re
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("headless upload test content")
            tmp_file = f.name
        try:
            page = Page__Send_SGraph_Ai__Upload()
            page.setup()
            token = page.upload_file(tmp_file)
            page.teardown()
            assert token, "upload_file() returned empty token"
            assert re.match(r"\b[a-z]+-[a-z]+-\d{4}\b", token), \
                f"Token does not match word-word-NNNN: {token!r}"
        finally:
            os.unlink(tmp_file)

    @pytest.mark.skip("requires browser — run manually")
    def test_current_logic(self):
        with self.upload_page as _:
            _.current_logic()

    @pytest.mark.skip("requires browser — run manually")
    def test_debug_setup_chrome(self):
        with self.upload_page as _:
            _.debug_setup_chrome()

    @pytest.mark.skip("doesn't work when running with all tests")
    def test_debug_inner_calls_of_setup(self):
        with self.upload_page as _:
            _.debug_inner_calls_of_setup()
            # >               raise Error(
            #                     """It looks like you are using Playwright Sync API inside the asyncio loop.
            #     Please use the Async API instead."""
            #                 )
            # E               playwright._impl._errors.Error: It looks like you are using Playwright Sync API inside the asyncio loop.
            # E               Please use the Async API instead.
            #
            # [LIB-2026-04-01-043] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md

    @pytest.mark.skip("requires browser — run manually")
    def test_debug_start_api_server(self):
        with self.upload_page as _:
            _.debug_start_api_server()

    @pytest.mark.skip("requires browser — run manually")
    def test_debug_start_api_server__with_saved_state(self):
        with self.upload_page as _:
            _.debug_start_api_server__with_saved_state()

    @pytest.mark.skip("requires browser — run manually")
    def test_debug_inner_methods_of__start_api_server(self):
        with self.upload_page as _:
            _.debug_inner_methods_of__start_api_server()

    @pytest.mark.skip("requires browser — run manually")
    def test_debug__start_and_stop_server_using_port(self):
        with self.upload_page as _:
            result = _.debug__start_and_stop_server_using_port()
            pid    = result.pid
            port   = result.port
            stderr = result.stderr
            stdout = result.stdout
            # [LIB-2026-04-01-044] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
            assert result == __(fast_api_process = __(_waitpid_lock=__SKIP__,
                                                      _input=None,
                                                      _communication_started=False,
                                                      args=[ 'poetry',
                                                             'run',
                                                             'uvicorn',
                                                             'sgraph_ai_app_send.lambda__user.lambda_function.lambda_handler__user:app',
                                                             '--port',
                                                             str(port),
                                                             '--log-level',
                                                             'info',
                                                             '--timeout-graceful-shutdown',
                                                             '0'],
                                                      stdin=None,
                                                      stdout=__SKIP__,
                                                      stderr=__SKIP__,
                                                      pid=pid,
                                                      returncode=None,
                                                      encoding=None,
                                                      errors=None,
                                                      pipesize=-1,
                                                      text_mode=None,
                                                      _sigint_wait_secs=0.25,
                                                      _closed_child_pipe_fds=True,
                                                      _child_created=True),
                                stderr      = stderr ,
                                stdout      = stdout ,
                                pid         = pid    ,
                                port        = port   ,
                                url__server       = f'http://localhost:{port}',
                                url__server__info = f'http://localhost:{port}/info/status' )

            #pprint(result.fast_api_process.stdout.flush())
            #pprint(result.fast_api_process.stdout.read())

            assert requests.get(result.url__server__info).status_code == 200    # confirm server is still up
            assert is_port_open('localhost', port)                    is True   # confirm port is open
            assert kill_process(pid)                                  is None   # [LIB-2026-04-01-045] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
            assert wait_for_port_closed('localhost', port)            is True   # wait until port is closed
            assert is_port_open('localhost', port) is False           is False  # confirm port is closed

            try:
                requests.get(result.url__server__info)                          #   try to make a request (which will fail with the exception below)
            except Exception as error:
                assert str(error.args[0].reason) == (f"HTTPConnection(host='localhost', port={port}): "
                                                     f"Failed to establish a new connection: [Errno 61] Connection refused")
        # [LIB-2026-04-01-046] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md


# ═══════════════════════════════════════════════════════════════════════════════
# Integration tests — require Chromium and a running SG/Send instance; skip in CI
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.skip("requires browser — run manually")
class test_Page__Send_SGraph_Ai__Upload__Integration(TestCase):
    """Integration tests for Page__Send_SGraph_Ai__Upload — browser required.

    These tests exercise the full upload flow through a real headless Chromium
    browser against a running SG/Send instance.  They are skipped in CI because
    Chromium is not available in the sandbox; run them locally with:

        pytest tests/qa/apis_for_sites/send_sgraph_ai/pages/ -k Integration -s
    """

    @classmethod
    def setUpClass(cls):
        import os, re, tempfile
        cls._os             = os
        cls._re             = re
        cls._token_pattern  = re.compile(r"\b[a-z]+-[a-z]+-\d{4}\b")
        cls.page            = Page__Send_SGraph_Ai__Upload()
        cls.page.setup()

        # Create a small temp file once — reused across tests in this class
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("SG/Send QA integration test — upload via Page__Send_SGraph_Ai__Upload.")
            cls._tmp_file = f.name

        # Perform the upload once; store the token for all assertions
        cls._token = cls.page.upload_file(cls._tmp_file)

    @classmethod
    def tearDownClass(cls):
        cls.page.teardown()
        if hasattr(cls, '_tmp_file') and cls._os.path.exists(cls._tmp_file):
            cls._os.unlink(cls._tmp_file)

    def test_upload_file__returns_friendly_token(self):                          # upload_file() must return a non-empty friendly token
        assert self._token, "upload_file() returned an empty string — expected a friendly token"
        assert isinstance(self._token, str), f"upload_file() must return str, got {type(self._token)}"
        assert self._token_pattern.search(self._token), (
            f"Token does not match word-word-NNNN pattern: {self._token!r}"
        )

    def test_get_friendly_token__after_upload(self):                             # get_friendly_token() must return the same token as upload_file()
        page_token = self.page.get_friendly_token()
        assert page_token, "get_friendly_token() returned an empty string after upload"
        assert self._token_pattern.search(page_token), (
            f"get_friendly_token() result does not match word-word-NNNN pattern: {page_token!r}"
        )
        assert page_token == self._token, (
            f"get_friendly_token() returned {page_token!r} but upload_file() returned {self._token!r} — they must match"
        )

    def test_upload_page__is_accessible(self):                                   # root page loaded successfully — basic smoke check
        assert self.page.harness         is not None, "harness must be set after setup()"
        assert self.page.sg_send         is not None, "sg_send must be set after setup()"
        assert self.page.config.headless is True,     "headless must default to True (CI safety)"
