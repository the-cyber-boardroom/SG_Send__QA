"""Unit tests for State_Transition (pure data class)."""
from unittest import TestCase

from sg_send_qa.state_machines.primitives       import Safe_Str__State_Name, Safe_Str__Trigger_Name
from sg_send_qa.state_machines.State_Transition import State_Transition


class test_State_Transition(TestCase):

    def test__defaults_are_empty_strings(self):
        t = State_Transition()
        assert str(t.from_state) == ''
        assert str(t.to_state)   == ''
        assert str(t.trigger)    == ''
        assert str(t.guard)      == ''
        assert str(t.security)   == ''

    def test__constructor_kwargs_accepted(self):
        t = State_Transition(from_state='idle', to_state='file-ready',
                             trigger='file_selected', guard='file_input_has_file')
        assert str(t.from_state) == 'idle'
        assert str(t.to_state)   == 'file-ready'
        assert str(t.trigger)    == 'file_selected'
        assert str(t.guard)      == 'file_input_has_file'

    def test__types_are_safe_str_subclasses(self):
        t = State_Transition(from_state='idle', to_state='complete')
        assert isinstance(t.from_state, Safe_Str__State_Name)
        assert isinstance(t.to_state,   Safe_Str__State_Name)

    def test__json_round_trip(self):
        t = State_Transition(from_state='confirming', to_state='encrypting',
                             trigger='click_encrypt_upload', security='plaintext_in_memory')
        data      = t.json()
        restored  = State_Transition.from_json(data)
        assert str(restored.from_state) == 'confirming'
        assert str(restored.to_state)   == 'encrypting'
        assert str(restored.trigger)    == 'click_encrypt_upload'
        assert str(restored.security)   == 'plaintext_in_memory'
        assert isinstance(restored.from_state, Safe_Str__State_Name)

    def test__json_keys(self):
        t    = State_Transition(from_state='a', to_state='b')
        keys = set(t.json().keys())
        assert keys == {'from_state', 'to_state', 'trigger', 'guard', 'security'}
