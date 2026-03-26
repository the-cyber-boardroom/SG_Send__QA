"""Unit tests for QA_API__Session — record_transition and transitions_observed."""
from unittest import TestCase

from sg_send_qa.api.QA_API__Session         import QA_API__Session
from sg_send_qa.api.Schema__QA_Request      import Schema__QA_Request
from sg_send_qa.api.Schema__Transition_Observed import Schema__Transition_Observed


class test_QA_API__Session(TestCase):

    def setUp(self):
        self.session = QA_API__Session(request=Schema__QA_Request())

    def test__transitions_observed_defaults_empty(self):
        assert list(self.session.transitions_observed) == []

    def test__record_transition__appends_entry(self):
        self.session.record_transition('idle', 'file-ready', 'file_selected')
        assert len(self.session.transitions_observed) == 1
        entry = self.session.transitions_observed[0]
        assert isinstance(entry, Schema__Transition_Observed)
        assert entry.from_state == 'idle'
        assert entry.to_state   == 'file-ready'
        assert entry.trigger    == 'file_selected'

    def test__record_transition__trigger_optional(self):
        self.session.record_transition('confirming', 'encrypting')
        entry = self.session.transitions_observed[0]
        assert entry.trigger == ''

    def test__record_transition__accumulates_multiple(self):
        self.session.record_transition('idle',       'file-ready',      'file_selected')
        self.session.record_transition('file-ready', 'choosing-share',  'single_file')
        self.session.record_transition('confirming', 'encrypting',      'confirm_click')
        assert len(self.session.transitions_observed) == 3
        assert self.session.transitions_observed[2].from_state == 'confirming'

    def test__record_transition__returns_none(self):
        result = self.session.record_transition('idle', 'file-ready')
        assert result is None
