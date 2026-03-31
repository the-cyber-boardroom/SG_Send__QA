from osbot_utils.helpers.duration.decorators.print_duration import print_duration
from osbot_utils.testing.Stderr import Stderr
from osbot_utils.type_safe.Type_Safe import Type_Safe

from sg_send_qa.browser.SG_Send__Browser__Test_Harness import SG_Send__Browser__Test_Harness


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

        with print_duration(action_name="setup SG_Send__Browser__Test_Harness"): # todo: this is a better description for what is happening
            with self.harness as _:
                saved_state =  _._load_saved_state()
                _._start_api_server(saved_state)
                _._build_ui(saved_state)
                _._start_ui_server(saved_state)
                _._create_browser()
                _._save_state()
                if _.config.capture_stderr:
                    _.stderr = Stderr()
                    _.stderr.start()
        self.harness.teardown()

# todo: here is that the duration of the code above is (consistent with what we want do debug)
# action "setup SG_Send__Browser__Test_Harness" took: 0.311 seconds
# action "setup SG_Send__Browser__Test_Harness" took: 0.313 seconds
# action "setup SG_Send__Browser__Test_Harness" took: 0.313 seconds