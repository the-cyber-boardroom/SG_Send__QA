from unittest                                       import TestCase
from osbot_utils.utils.Files                        import folder_exists, file_exists
from osbot_utils.utils.Misc                         import random_port
from sg_send_qa.browser.Harness_State__Persistence  import Harness_State__Persistence
from sg_send_qa.browser.Schema__Harness_State       import Schema__Harness_State


class test_Harness_State__Persistence(TestCase):                                # Unit tests — file operations

    @classmethod
    def setUpClass(cls):
        cls.persistence = Harness_State__Persistence()
        cls.persistence.clear()                                                 # start clean

    @classmethod
    def tearDownClass(cls):
        cls.persistence.clear()                                                 # clean up after

    # ── State folder ─────────────────────────────────────────────────────────

    def test_state_folder(self):
        folder = self.persistence.state_folder()
        assert folder_exists(folder)
        assert 'sg_send_qa_harness' in folder

    def test_state_file(self):
        path = self.persistence.state_file()
        assert 'harness_state.json' in path
        assert 'sg_send_qa_harness' in path

    # ── Save / Load / Clear ──────────────────────────────────────────────────

    def test_exists__before_save(self):
        self.persistence.clear()
        assert self.persistence.exists() is False

    def test_load__before_save(self):
        self.persistence.clear()
        assert self.persistence.load() is None

    def test_save_and_load(self):
        state = Schema__Harness_State(api_port        = 54321              ,
                                      ui_port         = 63960              ,
                                      ui_build_folder = '/tmp/test_build'  ,
                                      ui_version      = 'v0.2.18'         ,
                                      access_token    = 'abc-123-token'    ,
                                      chrome_port     = 10070              )
        self.persistence.save(state)

        assert self.persistence.exists() is True
        assert file_exists(self.persistence.state_file())

        loaded = self.persistence.load()
        assert type(loaded)          is Schema__Harness_State
        assert loaded.api_port        == 54321
        assert loaded.ui_port         == 63960
        assert loaded.ui_build_folder == '/tmp/test_build'
        assert loaded.ui_version      == 'v0.2.18'
        assert loaded.access_token    == 'abc-123-token'
        assert loaded.chrome_port     == 10070

    def test_save__overwrites_previous(self):
        state_1 = Schema__Harness_State(api_port=11111, ui_port=22222)
        state_2 = Schema__Harness_State(api_port=33333, ui_port=44444)

        self.persistence.save(state_1)
        assert self.persistence.load().api_port == 11111

        self.persistence.save(state_2)
        assert self.persistence.load().api_port == 33333                        # overwritten, not appended

    def test_clear(self):
        state = Schema__Harness_State(api_port=99999)
        self.persistence.save(state)
        assert self.persistence.exists() is True

        self.persistence.clear()
        assert self.persistence.exists() is False
        assert self.persistence.load()   is None

    # ── Port checks ──────────────────────────────────────────────────────────

    def test_ports_available__unused_ports(self):                                # ports nobody is listening on
        state = Schema__Harness_State(api_port = random_port()  ,
                                      ui_port  = random_port()  )
        assert self.persistence.ports_available(state) is True

    def test_ports_in_use__unused_ports(self):                                  # no servers running → not in use
        state = Schema__Harness_State(api_port = random_port()  ,
                                      ui_port  = random_port()  )
        assert self.persistence.ports_in_use(state) is False

    # ── Port allocation ──────────────────────────────────────────────────────

    def test_allocate_ports__no_saved_state(self):                              # first run — gets random ports
        api_port, ui_port = self.persistence.allocate_ports(None)
        assert api_port > 0
        assert ui_port  > 0
        assert api_port != ui_port

    def test_allocate_ports__reuses_saved(self):                                # second run — reuses saved ports
        state = Schema__Harness_State(api_port = 54321 ,
                                      ui_port  = 63960 )
        api_port, ui_port = self.persistence.allocate_ports(state)
        assert api_port == 54321
        assert ui_port  == 63960

    # ── Round-trip ───────────────────────────────────────────────────────────

    def test_full_round_trip(self):                                             # save → load → allocate → verify same ports
        self.persistence.clear()

        api_port = random_port()
        ui_port  = random_port()

        state = Schema__Harness_State(api_port        = api_port               ,
                                      ui_port         = ui_port                ,
                                      ui_build_folder = '/tmp/qa_build_test'   ,
                                      ui_version      = 'v0.2.18'             ,
                                      access_token    = 'round-trip-token'     ,
                                      chrome_port     = 10070                  )
        self.persistence.save(state)

        loaded = self.persistence.load()
        assert loaded.api_port     == api_port
        assert loaded.ui_port      == ui_port
        assert loaded.access_token == 'round-trip-token'

        new_api, new_ui = self.persistence.allocate_ports(loaded)               # ports are free → reuse them
        assert new_api == api_port
        assert new_ui  == ui_port

        self.persistence.clear()