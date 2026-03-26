"""Unit tests for State_Machine__Snapshot and State_Machine__Utils.build_snapshot()."""
from unittest import TestCase

from sg_send_qa.state_machines.State_Machine__Download  import download_state_machine
from sg_send_qa.state_machines.State_Machine__Snapshot  import State_Machine__Snapshot
from sg_send_qa.state_machines.State_Machine__Upload    import upload_state_machine
from sg_send_qa.state_machines.State_Machine__Utils     import State_Machine__Utils
from sg_send_qa.state_machines.State_Transition         import State_Transition


class test_State_Machine__Snapshot(TestCase):

    def setUp(self):
        self.utils    = State_Machine__Utils()
        self.upload   = upload_state_machine()
        self.download = download_state_machine()

    # --------------------------------------------------------- schema defaults

    def test__snapshot_fields(self):
        snap = State_Machine__Snapshot()
        keys = list(snap.json().keys())
        for field in ['version', 'timestamp', 'state_machine',
                      'states_found', 'transitions_observed',
                      'transitions_expected', 'missing', 'unexpected']:
            assert field in keys, f"Missing field: {field}"

    def test__timestamp_is_nonzero(self):
        snap = State_Machine__Snapshot()
        assert int(snap.timestamp) > 0                          # Timestamp_Now initialises to UTC ms

    def test__json_round_trip(self):
        snap  = State_Machine__Snapshot(version='v0.3.0', state_machine='upload_wizard')
        data  = snap.json()
        assert data['version']       == 'v0.3.0'
        assert data['state_machine'] == 'upload_wizard'
        assert 'timestamp'           in data

    # --------------------------------------------------------- build_snapshot

    def test__full_coverage_snapshot(self):
        all_pairs = [(str(t.from_state), str(t.to_state)) for t in self.upload.transitions]
        snap = self.utils.build_snapshot(self.upload, all_pairs, version='v0.3.0')
        assert str(snap.state_machine)         == 'upload_wizard'
        assert str(snap.version)               == 'v0.3.0'
        assert len(list(snap.missing))         == 0
        assert len(list(snap.unexpected))      == 0
        assert len(list(snap.transitions_observed)) == len(all_pairs)

    def test__zero_coverage_snapshot(self):
        snap = self.utils.build_snapshot(self.upload, [], version='v0.3.0')
        assert len(list(snap.missing))              == len(self.upload.transitions)
        assert len(list(snap.transitions_observed)) == 0
        assert len(list(snap.unexpected))           == 0

    def test__partial_coverage__missing_and_states_found(self):
        observed = [('idle', 'file-ready'), ('confirming', 'encrypting')]
        snap     = self.utils.build_snapshot(self.upload, observed, version='v0.3.0')
        assert len(list(snap.transitions_observed)) == 2
        assert len(list(snap.missing))              == len(self.upload.transitions) - 2
        states = [str(s) for s in snap.states_found]
        assert 'idle'       in states
        assert 'file-ready' in states
        assert 'encrypting' in states

    def test__unexpected_transition_detected(self):
        """An observed pair not in the definition is flagged as unexpected."""
        bogus_pairs = [('idle', 'complete')]                    # not a valid upload transition
        snap = self.utils.build_snapshot(self.upload, bogus_pairs, version='v0.3.0')
        unexpected = [(str(t.from_state), str(t.to_state)) for t in snap.unexpected]
        assert ('idle', 'complete') in unexpected

    def test__transitions_expected_matches_machine(self):
        snap = self.utils.build_snapshot(self.upload, [], version='v0.3.0')
        assert len(list(snap.transitions_expected)) == len(self.upload.transitions)
        expected_pairs = [(str(t.from_state), str(t.to_state)) for t in snap.transitions_expected]
        defined_pairs  = [(str(t.from_state), str(t.to_state)) for t in self.upload.transitions]
        assert set(expected_pairs) == set(defined_pairs)

    def test__missing_are_state_transition_instances(self):
        snap = self.utils.build_snapshot(self.upload, [], version='v0.3.0')
        for t in snap.missing:
            assert isinstance(t, State_Transition)

    def test__snapshot_json_is_serialisable(self):
        """Full snapshot serialises without error (nested Type_Safe lists)."""
        import json
        observed = [('idle', 'file-ready'), ('file-ready', 'choosing-share')]
        snap     = self.utils.build_snapshot(self.upload, observed, version='v0.3.0')
        data     = snap.json()
        raw      = json.dumps(data)                             # must not raise
        assert '"upload_wizard"' in raw

    def test__download_snapshot(self):
        observed = [('loading', 'entry'), ('entry', 'ready'), ('ready', 'decrypting')]
        snap = self.utils.build_snapshot(self.download, observed, version='v0.3.0')
        assert str(snap.state_machine) == 'download_flow'
        states = [str(s) for s in snap.states_found]
        assert 'decrypting' in states
        # many download transitions are not yet observed
        assert len(list(snap.missing)) > 0
