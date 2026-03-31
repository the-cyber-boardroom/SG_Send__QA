from osbot_fast_api.utils.Fast_API_Server                                   import Fast_API_Server
from osbot_utils.helpers.duration.decorators.print_duration                 import print_duration
from osbot_utils.testing.Stderr                                             import Stderr
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                      import SG_Send__Browser__Test_Harness
from sg_send_qa.browser.Schema__Browser_Test_Config                         import Schema__Browser_Test_Config
from sgraph_ai_app_send.lambda__user.testing.Send__User_Lambda__Test_Server import setup__send_user_lambda__test_client


class Page__Send_SGraph_Ai__Upload(Type_Safe):
    #harness : SG_Send__Browser__Test_Harness

    def current_logic(self):
        with print_duration(action_name="setup harness"):
            self.harness = SG_Send__Browser__Test_Harness()
        with print_duration(action_name="setup chrome"):
            self.harness.headless(False).setup()
            self.sg_send = self.harness.sg_send
        with print_duration(action_name="set_access_token"):
            self.harness.set_access_token()
        with print_duration(action_name="open page root"):
            self.sg_send.page__root()

        with print_duration(action_name="close servers (but not chrome)"):
            self.harness.teardown()

# todo: I usually start with code like the above so that I can understand what is taking time
#       usually anything that takes more than 250ms needs investigation , since those are costs tha compound
#       and we should be looking at ways to optimise it


# todo: here is data from a couple executions of the code above
#
# action "setup harness" took: 0.0 seconds
# action "setup chrome" took: 0.243 seconds
# action "set_access_token" took: 0.856 seconds
# action "open page root" took: 0.108 seconds

# action "setup harness" took: 0.0 seconds
# action "setup chrome" took: 0.32 seconds
# action "set_access_token" took: 0.719 seconds
# action "open page root" took: 0.099 seconds

# action "setup harness" took: 0.0 seconds
# action "setup chrome" took: 0.303 seconds
# action "set_access_token" took: 0.678 seconds
# action "open page root" took: 0.093 seconds

# todo: so the duration of the test (in the last case) was 1.074 secs
#       which we can see that it was the setup chrome and set_access_token that is taking time
#       note that I already have a chrome running, so this is not the cost of staring a chrome process
#       .
#       first thing I'm going to look is at those 0.3 secs that it takes to connect and see if we can optimise that


    # todo: let's isolate this into a separate test
    def debug_setup_chrome(self):
        self.harness = SG_Send__Browser__Test_Harness()
        with print_duration(action_name="setup chrome"):
            self.harness.headless(False).setup()

        with print_duration(action_name="close servers (but not chrome)"):
            self.harness.teardown()

# todo: ok the reason I was having that issue when running this multple times is because of
#       not stopping these servers

# for reference stopping the servers takes about
#
# action "close servers (but not chrome)" took: 0.145 seconds
# action "close servers (but not chrome)" took: 0.104 seconds
# action "close servers (but not chrome)" took: 0.109 seconds

    def debug_inner_calls_of_setup(self):
        self.harness = SG_Send__Browser__Test_Harness()
        # ---- these are the exact methods that SG_Send__Browser__Test_Harness(),setup() will call

        #with print_duration(action_name="setup SG_Send__Browser__Test_Harness"): # todo: this is a better description for what is happening
        with self.harness as _:
            with print_duration(action_name ="_load_saved_state"):
                saved_state =  _._load_saved_state()
            with print_duration(action_name ="_start_api_server"):
                _._start_api_server(saved_state)
            with print_duration(action_name ="_build_ui"):
                _._build_ui(saved_state)
            with print_duration(action_name ="_start_ui_server"):
                _._start_ui_server(saved_state)
            with print_duration(action_name ="_create_browser"):
                _._create_browser()
            with print_duration(action_name ="_save_state"):
                _._save_state()
            with print_duration(action_name ="capture_stderr"):
                if _.config.capture_stderr:
                    _.stderr = Stderr()
                    _.stderr.start()

        self.harness.teardown()

# todo: (before adding the inner duration captures ) here is that the duration of the code above is (consistent with what we want do debug)
# action "setup SG_Send__Browser__Test_Harness" took: 0.311 seconds
# action "setup SG_Send__Browser__Test_Harness" took: 0.313 seconds
# action "setup SG_Send__Browser__Test_Harness" took: 0.313 seconds

# todo: here are the inner duration captures

# action "_load_saved_state" took: 0.0 seconds
# action "_start_api_server" took: 0.24 seconds
# action "_build_ui" took: 0.107 seconds
# action "_start_ui_server" took: 0.005 seconds
# action "_create_browser" took: 0.0 seconds
# action "_save_state" took: 0.0 seconds
# action "capture_stderr" took: 0.0 seconds

# action "_load_saved_state" took: 0.0 seconds
# action "_start_api_server" took: 0.222 seconds
# action "_build_ui" took: 0.103 seconds
# action "_start_ui_server" took: 0.003 seconds
# action "_create_browser" took: 0.0 seconds
# action "_save_state" took: 0.0 seconds
# action "capture_stderr" took: 0.0 seconds

# todo: from the data above we can see that the ones that explain the 300ms duration are
#
#      "_start_api_server"  with ~ 0.222 seconds
#      "_build_ui"          with ~ 0.103 seconds

# both we should be able to optimise

    def debug_start_api_server(self):
        with SG_Send__Browser__Test_Harness() as _:
            assert _.config.headless is True                                # this will disable the use of safe state
            assert _._load_saved_state() is None                            # confirm that save state is disabled by default
            with print_duration(action_name="start api server"):
                _._start_api_server()
            with print_duration(action_name="stop api server"):
                _.api_server.stop()

    # todo: here are the stats of this
    # action "start api server" took: 0.222 seconds
    # action "stop api server" took: 0.112 seconds

    # action "start api server" took: 0.215 seconds#
    # action "stop api server" took: 0.11 seconds

    def debug_start_api_server__with_saved_state(self):
        config = Schema__Browser_Test_Config(headless=False)        # todo: research to see if there is any code using Schema__Browser_Test_Config(headless=False) , which, thinking about it, is only used by me when debugging, which means that this might not be the best variable to control the use of safe state
        with SG_Send__Browser__Test_Harness(config=config) as _:
            with print_duration(action_name="load_saved_state"):
                saved_state = _._load_saved_state()                 # todo: see how this is working since this saved state needs Schema__Browser_Test_Config.headless=False to work

                #saved_state.print_obj()
                # todo: here are the values currently saved
                # __(api_port=44725,
                #    ui_port=53938,
                #    ui_build_folder='/var/folders/z4/3k99j_cn39g_0jnqt6w57f6m0000gn/T/sg_send_qa_ui_build_v0.2.46',
                #    ui_version='v0.2.46',
                #    access_token='ff4e8cf3-4286-48d3-a2c4-49b80a7f4867',
                #    chrome_port=10070)

                #print(_.persistence.state_file())
                # todo: here is the state file (saved in the sg_send_qa_harness folder inside the current temp folder)
                # /var/folders/z4/3k99j_cn39g_0jnqt6w57f6m0000gn/T/sg_send_qa_harness/harness_state.json


            with print_duration(action_name="start api server"):
                _._start_api_server(saved_state=saved_state)            # todo: inside _start_api_server , the saved_state is only used to set the api_port
            with print_duration(action_name="stop api server"):
                _.api_server.stop()


    def debug_inner_methods_of__start_api_server(self):

        with SG_Send__Browser__Test_Harness() as _:
            saved_state     = _._load_saved_state()                     # this is passed as a param to start_api_server
            with print_duration(action_name="setup__send_user_lambda__test_client"):
                self.test_objs  = setup__send_user_lambda__test_client()

            with print_duration(action_name="setup Fast_API_Server"):
                api_port        = saved_state.api_port if saved_state else 0            # 0 = let Fast_API_Server pick random
                self.api_server = Fast_API_Server(app  = self.test_objs.fast_api__app ,
                                                  port = api_port                      )

            with print_duration(action_name="start api server"):
                self.api_server.start()

            with print_duration(action_name="stop api server"):
                self.api_server.stop()

        # todo: is the data from the execution above
        #
        # action "setup__send_user_lambda__test_client" took: 0.115 seconds
        # action "setup Fast_API_Server" took: 0.0 seconds
        # action "start api server" took: 0.105 seconds
        # action "stop api server" took: 0.112 seconds

        # action "setup__send_user_lambda__test_client" took: 0.124 seconds
        # action "setup Fast_API_Server" took: 0.0 seconds
        # action "start api server" took: 0.103 seconds
        # action "stop api server" took: 0.114 seconds

        # which is basically
        #       ~120ms for setup__send_user_lambda__test_client
        #       ~110ms for start api server
        #       ~110ms for stop api server

# todo: so the key challenge is here is that we can only stop the server using the current method
#       if we have fast_api server process object (which we do)
#       but if we start the server in one test execution we won't have this object
#       in the past I solved similar problems (for example with long lived chrome process)
#       by also storing the process id
#       this way we can kill that process later
#
#       having this server up (and control it when it is up, not only will save us 300ms per test class execution (which adds up as we have more and more tests)
#       will also allow us to configure that server once (for example to add multiple
#           - test files (of all types and size)
#           - vaults
#           - access and (eventually) PKI keys
