# ═══════════════════════════════════════════════════════════════════════════════
# SG/Send QA — Persistent Harness State
# Saves server ports, build folder, and access token to a JSON config file
# so that servers restart on the same ports across runs.
#
# Pattern borrowed from OSBot-Playwright's Playwright_Process:
#   - save_process_details() → JSON file at well-known path
#   - load_process_details() → check if PID alive, reconnect or restart
#
# Why: when the UI server port stays the same, localStorage persists (same
# origin). When the API port stays the same, build-info.js doesn't change.
# This means set_access_token() is usually a no-op, and individual test
# steps can be re-run without "Failed to fetch" errors.
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_utils.utils.Files                        import path_combine, temp_folder_current, folder_create, file_exists
from osbot_utils.utils.Json                         import json_save_file, json_load_file
from osbot_utils.utils.Misc                         import random_port
from osbot_utils.utils.Http                         import port_is_open

from sg_send_qa.browser.Schema__Harness_State import Schema__Harness_State

HARNESS_STATE_FOLDER = 'sg_send_qa_harness'
HARNESS_STATE_FILE   = 'harness_state.json'




class Harness_State__Persistence(Type_Safe):                                    # load/save harness state from disk

    def state_folder(self):                                                     # well-known temp path
        path = path_combine(temp_folder_current(), HARNESS_STATE_FOLDER)
        folder_create(path)
        return path

    def state_file(self):                                                       # path to the JSON file
        return path_combine(self.state_folder(), HARNESS_STATE_FILE)

    def exists(self):                                                           # is there a saved state?
        return file_exists(self.state_file())

    def save(self, state: Schema__Harness_State):                               # persist state to disk
        data = dict(api_port        = state.api_port        ,
                    ui_port         = state.ui_port         ,
                    ui_build_folder = state.ui_build_folder ,
                    ui_version      = state.ui_version      ,
                    access_token    = state.access_token    ,
                    chrome_port     = state.chrome_port     )
        json_save_file(data, self.state_file())
        return self

    def load(self) -> Schema__Harness_State:                                    # load state from disk, return None if missing/invalid
        if not self.exists():
            return None
        try:
            data = json_load_file(self.state_file())
            return Schema__Harness_State(**data)
        except Exception:
            return None

    def clear(self):                                                            # delete saved state (force fresh start)
        from osbot_utils.utils.Files import file_delete
        file_delete(self.state_file())
        return self

    def ports_available(self, state: Schema__Harness_State):                    # check if saved ports are free (not hijacked by another process)
        api_free = not port_is_open('localhost', state.api_port)                # port should be FREE (server not running)
        ui_free  = not port_is_open('localhost', state.ui_port)
        return api_free and ui_free

    def ports_in_use(self, state: Schema__Harness_State):                       # check if servers are still running (stale process detection)
        api_alive = port_is_open('localhost', state.api_port)
        ui_alive  = port_is_open('localhost', state.ui_port)
        return api_alive or ui_alive

    def allocate_ports(self, existing_state=None):                              # allocate ports: reuse saved if free, else pick new
        if existing_state and self.ports_available(existing_state):
            return existing_state.api_port, existing_state.ui_port              # reuse — same ports as last run
        return random_port(), random_port()                                     # fresh — random available ports