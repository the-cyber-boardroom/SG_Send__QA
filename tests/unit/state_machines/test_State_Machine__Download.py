"""Unit tests for State_Machine__Download."""
from unittest import TestCase

from sg_send_qa.state_machines.State_Machine__Download import State_Machine__Download, download_state_machine
from sg_send_qa.state_machines.State_Transition        import State_Transition


class test_State_Machine__Download(TestCase):

    def setUp(self):
        self.sm = download_state_machine()

    def test__name(self):
        assert str(self.sm.name) == 'download_flow'

    def test__states_count(self):
        assert len(self.sm.states) == 9

    def test__states_include_expected(self):
        states = [str(s) for s in self.sm.states]
        for expected in ['loading', 'entry', 'ready', 'decrypting',
                         'complete', 'error', 'browse', 'gallery', 'viewer']:
            assert expected in states, f"Missing state: {expected}"

    def test__three_branches_from_loading(self):
        from_loading = [t for t in self.sm.transitions
                        if str(t.from_state) == 'loading']
        assert len(from_loading) == 3
        targets = {str(t.to_state) for t in from_loading}
        assert targets == {'entry', 'ready', 'error'}

    def test__three_auto_routes_from_ready(self):
        auto_routes = [t for t in self.sm.transitions
                       if str(t.from_state) == 'ready' and str(t.trigger) == 'auto_route']
        assert len(auto_routes) == 3
        targets = {str(t.to_state) for t in auto_routes}
        assert targets == {'browse', 'gallery', 'viewer'}

    def test__entry_self_loop(self):
        """entry → entry when bogus token submitted (inline error stays on form)."""
        self_loops = [t for t in self.sm.transitions
                      if str(t.from_state) == 'entry' and str(t.to_state) == 'entry']
        assert len(self_loops) == 1
        assert str(self_loops[0].trigger) == 'submit_bogus'

    def test__decrypt_outcomes(self):
        from_decrypting = {str(t.to_state) for t in self.sm.transitions
                           if str(t.from_state) == 'decrypting'}
        assert from_decrypting == {'complete', 'error'}

    def test__security_annotations_present(self):
        tags = {str(t.security) for t in self.sm.transitions if t.security}
        assert 'key_in_memory'    in tags
        assert 'plaintext_in_dom' in tags

    def test__json_round_trip(self):
        data     = self.sm.json()
        restored = State_Machine__Download.from_json(data)
        assert str(restored.name) == 'download_flow'
        assert len(restored.states)      == len(self.sm.states)
        assert len(restored.transitions) == len(self.sm.transitions)
        assert isinstance(restored.transitions[0], State_Transition)
