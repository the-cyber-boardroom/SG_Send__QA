"""Unit tests for State_Machine__Upload."""
from unittest import TestCase

from sg_send_qa.state_machines.State_Machine__Upload import State_Machine__Upload, upload_state_machine
from sg_send_qa.state_machines.State_Transition      import State_Transition


class test_State_Machine__Upload(TestCase):

    def setUp(self):
        self.sm = upload_state_machine()

    def test__name(self):
        assert str(self.sm.name) == 'upload_wizard'

    def test__states_count(self):
        assert len(self.sm.states) == 9

    def test__states_include_expected(self):
        states = [str(s) for s in self.sm.states]
        for expected in ['idle', 'file-ready', 'choosing-share', 'confirming',
                         'encrypting', 'uploading', 'completing', 'complete']:
            assert expected in states, f"Missing state: {expected}"

    def test__transitions_are_State_Transition_objects(self):
        assert len(self.sm.transitions) > 0
        for t in self.sm.transitions:
            assert isinstance(t, State_Transition), f"Expected State_Transition, got {type(t)}"

    def test__transitions_count(self):
        assert len(self.sm.transitions) == 9

    def test__branch_from_file_ready(self):
        """file-ready has two outgoing edges (the delivery-step branch)."""
        from_file_ready = [t for t in self.sm.transitions
                           if str(t.from_state) == 'file-ready']
        assert len(from_file_ready) == 2
        targets = {str(t.to_state) for t in from_file_ready}
        assert targets == {'choosing-delivery', 'choosing-share'}

    def test__security_annotations_present(self):
        security_tagged = [t for t in self.sm.transitions if t.security]
        assert len(security_tagged) >= 2
        tags = {str(t.security) for t in security_tagged}
        assert 'plaintext_in_memory' in tags
        assert 'ciphertext_only'     in tags

    def test__json_round_trip(self):
        data     = self.sm.json()
        restored = State_Machine__Upload.from_json(data)
        assert str(restored.name) == 'upload_wizard'
        assert len(restored.states)      == len(self.sm.states)
        assert len(restored.transitions) == len(self.sm.transitions)
        assert isinstance(restored.transitions[0], State_Transition)

    def test__json_structure(self):
        data = self.sm.json()
        assert 'name'        in data
        assert 'states'      in data
        assert 'transitions' in data
        assert isinstance(data['states'],      list)
        assert isinstance(data['transitions'], list)
        first = data['transitions'][0]
        assert 'from_state' in first
        assert 'to_state'   in first
