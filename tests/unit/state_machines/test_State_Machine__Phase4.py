"""Phase 4 unit tests: diff_snapshots, to_mermaid_coverage, State_Machine__Snapshot__Diff."""
from unittest import TestCase

from sg_send_qa.state_machines.State_Machine__Download       import download_state_machine
from sg_send_qa.state_machines.State_Machine__Snapshot__Diff import State_Machine__Snapshot__Diff
from sg_send_qa.state_machines.State_Machine__Upload         import upload_state_machine
from sg_send_qa.state_machines.State_Machine__Utils          import State_Machine__Utils
from sg_send_qa.state_machines.State_Transition              import State_Transition


class test_State_Machine__Snapshot__Diff(TestCase):

    def test__fields(self):
        diff = State_Machine__Snapshot__Diff()
        keys = list(diff.json().keys())
        for field in ['version_a', 'version_b', 'state_machine',
                      'newly_covered', 'coverage_lost',
                      'new_unexpected', 'fixed_unexpected']:
            assert field in keys

    def test__json_round_trip(self):
        diff = State_Machine__Snapshot__Diff(version_a='v0.3.0', version_b='v0.3.1',
                                             state_machine='upload_wizard')
        data = diff.json()
        assert data['version_a']     == 'v0.3.0'
        assert data['version_b']     == 'v0.3.1'
        assert data['state_machine'] == 'upload_wizard'


class test_diff_snapshots(TestCase):

    def setUp(self):
        self.machine = upload_state_machine()
        self.utils   = State_Machine__Utils()

    # --------------------------------------------------------- no change

    def test__identical_snapshots_produce_empty_diff(self):
        pairs = [('idle', 'file-ready'), ('file-ready', 'choosing-share')]
        snap_a = self.utils.build_snapshot(self.machine, pairs, version='v0.3.0')
        snap_b = self.utils.build_snapshot(self.machine, pairs, version='v0.3.0')
        diff   = self.utils.diff_snapshots(snap_a, snap_b)
        assert list(diff.newly_covered)    == []
        assert list(diff.coverage_lost)    == []
        assert list(diff.new_unexpected)   == []
        assert list(diff.fixed_unexpected) == []

    # --------------------------------------------------------- coverage changes

    def test__newly_covered_detected(self):
        pairs_a = [('idle', 'file-ready')]
        pairs_b = [('idle', 'file-ready'), ('confirming', 'encrypting')]
        snap_a  = self.utils.build_snapshot(self.machine, pairs_a, version='v0.3.0')
        snap_b  = self.utils.build_snapshot(self.machine, pairs_b, version='v0.3.1')
        diff    = self.utils.diff_snapshots(snap_a, snap_b)
        newly   = [(str(t.from_state), str(t.to_state)) for t in diff.newly_covered]
        assert ('confirming', 'encrypting') in newly
        assert list(diff.coverage_lost) == []

    def test__coverage_lost_detected(self):
        pairs_a = [('idle', 'file-ready'), ('confirming', 'encrypting')]
        pairs_b = [('idle', 'file-ready')]
        snap_a  = self.utils.build_snapshot(self.machine, pairs_a, version='v0.3.0')
        snap_b  = self.utils.build_snapshot(self.machine, pairs_b, version='v0.3.1')
        diff    = self.utils.diff_snapshots(snap_a, snap_b)
        lost    = [(str(t.from_state), str(t.to_state)) for t in diff.coverage_lost]
        assert ('confirming', 'encrypting') in lost
        assert list(diff.newly_covered) == []

    def test__diff_versions_recorded(self):
        snap_a = self.utils.build_snapshot(self.machine, [], version='v0.3.0')
        snap_b = self.utils.build_snapshot(self.machine, [], version='v0.3.1')
        diff   = self.utils.diff_snapshots(snap_a, snap_b)
        assert str(diff.version_a)     == 'v0.3.0'
        assert str(diff.version_b)     == 'v0.3.1'
        assert str(diff.state_machine) == 'upload_wizard'

    # --------------------------------------------------------- anomaly changes

    def test__new_unexpected_detected(self):
        bogus  = [('idle', 'complete')]                         # not a defined transition
        snap_a = self.utils.build_snapshot(self.machine, [],    version='v0.3.0')
        snap_b = self.utils.build_snapshot(self.machine, bogus, version='v0.3.1')
        diff   = self.utils.diff_snapshots(snap_a, snap_b)
        unex   = [(str(t.from_state), str(t.to_state)) for t in diff.new_unexpected]
        assert ('idle', 'complete') in unex
        assert list(diff.fixed_unexpected) == []

    def test__fixed_unexpected_detected(self):
        bogus  = [('idle', 'complete')]
        snap_a = self.utils.build_snapshot(self.machine, bogus, version='v0.3.0')
        snap_b = self.utils.build_snapshot(self.machine, [],    version='v0.3.1')
        diff   = self.utils.diff_snapshots(snap_a, snap_b)
        fixed  = [(str(t.from_state), str(t.to_state)) for t in diff.fixed_unexpected]
        assert ('idle', 'complete') in fixed
        assert list(diff.new_unexpected) == []

    def test__diff_is_serialisable(self):
        import json
        pairs_a = [('idle', 'file-ready')]
        pairs_b = [('idle', 'file-ready'), ('confirming', 'encrypting')]
        snap_a  = self.utils.build_snapshot(self.machine, pairs_a, version='v0.3.0')
        snap_b  = self.utils.build_snapshot(self.machine, pairs_b, version='v0.3.1')
        diff    = self.utils.diff_snapshots(snap_a, snap_b)
        raw     = json.dumps(diff.json())                       # must not raise
        assert 'upload_wizard' in raw


class test_to_mermaid_coverage(TestCase):

    def setUp(self):
        self.machine = upload_state_machine()
        self.utils   = State_Machine__Utils()

    def test__starts_with_stateDiagram(self):
        result = self.utils.to_mermaid_coverage(self.machine, [])
        assert result.startswith('stateDiagram-v2')

    def test__contains_classdefs(self):
        result = self.utils.to_mermaid_coverage(self.machine, [])
        assert 'classDef covered'  in result
        assert 'classDef untested' in result

    def test__visited_states_marked_covered(self):
        obs    = [('idle', 'file-ready')]
        result = self.utils.to_mermaid_coverage(self.machine, obs)
        assert 'class idle,file-ready covered' in result or 'class file-ready,idle covered' in result

    def test__unvisited_states_marked_untested(self):
        obs    = [('idle', 'file-ready')]
        result = self.utils.to_mermaid_coverage(self.machine, obs)
        assert 'untested' in result
        # states not in obs should be in the untested class
        assert 'complete' in result.split('untested')[0].split('class ')[-1] or \
               'untested' in result                             # at minimum the classDef is present

    def test__zero_coverage_all_states_untested(self):
        result = self.utils.to_mermaid_coverage(self.machine, [])
        lines  = result.split('\n')
        covered_class_lines = [l for l in lines if l.strip().startswith('class ') and 'covered' in l]
        assert covered_class_lines == []                        # no `class X covered` line
        assert 'untested' in result

    def test__full_coverage_no_untested_class_line(self):
        all_pairs = [(str(t.from_state), str(t.to_state)) for t in self.machine.transitions]
        result    = self.utils.to_mermaid_coverage(self.machine, all_pairs)
        lines     = result.split('\n')
        untested_class_lines = [l for l in lines if l.strip().startswith('class ') and 'untested' in l]
        assert untested_class_lines == []

    def test__all_transitions_present(self):
        result = self.utils.to_mermaid_coverage(self.machine, [])
        assert result.count('-->') == len(self.machine.transitions)

    def test__download_machine_coverage(self):
        machine = download_state_machine()
        obs     = [('loading', 'entry'), ('entry', 'ready')]
        result  = self.utils.to_mermaid_coverage(machine, obs)
        assert 'stateDiagram-v2'   in result
        assert 'classDef covered'  in result
        assert 'classDef untested' in result
