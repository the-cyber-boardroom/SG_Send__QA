"""Unit tests for State_Machine__Utils (logic layer)."""
from unittest import TestCase

from sg_send_qa.state_machines.State_Machine__Download import download_state_machine
from sg_send_qa.state_machines.State_Machine__Upload   import upload_state_machine
from sg_send_qa.state_machines.State_Machine__Utils    import State_Machine__Utils


class test_State_Machine__Utils(TestCase):

    def setUp(self):
        self.utils    = State_Machine__Utils()
        self.upload   = upload_state_machine()
        self.download = download_state_machine()

    # --------------------------------------------------------- validate_transition

    def test__valid_transition_returns_true(self):
        assert self.utils.validate_transition(self.upload, 'idle', 'file-ready')         is True
        assert self.utils.validate_transition(self.upload, 'confirming', 'encrypting')   is True
        assert self.utils.validate_transition(self.download, 'loading', 'entry')         is True
        assert self.utils.validate_transition(self.download, 'decrypting', 'complete')   is True

    def test__invalid_transition_returns_false(self):
        assert self.utils.validate_transition(self.upload, 'idle', 'complete')           is False
        assert self.utils.validate_transition(self.upload, 'complete', 'idle')           is False
        assert self.utils.validate_transition(self.download, 'loading', 'complete')      is False

    def test__self_loop_valid(self):
        assert self.utils.validate_transition(self.download, 'entry', 'entry')           is True

    # --------------------------------------------------------- reachable_states

    def test__reachable_from_loading(self):
        reachable = set(self.utils.reachable_states(self.download, 'loading'))
        assert reachable == {'entry', 'ready', 'error'}

    def test__reachable_from_file_ready(self):
        reachable = set(self.utils.reachable_states(self.upload, 'file-ready'))
        assert reachable == {'choosing-delivery', 'choosing-share'}

    # --------------------------------------------------------- to_mermaid

    def test__to_mermaid_starts_with_stateDiagram(self):
        mermaid = self.utils.to_mermaid(self.upload)
        assert mermaid.startswith('stateDiagram-v2')

    def test__to_mermaid_contains_all_transitions(self):
        mermaid = self.utils.to_mermaid(self.upload)
        assert 'idle --> file-ready' in mermaid
        assert 'confirming --> encrypting' in mermaid
        assert 'encrypting --> uploading' in mermaid

    def test__to_mermaid_download_includes_branches(self):
        mermaid = self.utils.to_mermaid(self.download)
        assert 'loading --> entry'      in mermaid
        assert 'loading --> ready'      in mermaid
        assert 'loading --> error'      in mermaid
        assert 'ready --> browse'       in mermaid
        assert 'ready --> gallery'      in mermaid
        assert 'ready --> viewer'       in mermaid

    # --------------------------------------------------------- coverage

    def test__full_coverage(self):
        all_pairs = [(str(t.from_state), str(t.to_state))
                     for t in self.upload.transitions]
        result = self.utils.coverage(self.upload, all_pairs)
        assert result['coverage_pct'] == 100
        assert result['covered']      == result['total']
        assert result['missing']      == []

    def test__zero_coverage(self):
        result = self.utils.coverage(self.upload, [])
        assert result['coverage_pct'] == 0
        assert result['covered']      == 0
        assert len(result['missing']) == result['total']

    def test__partial_coverage(self):
        observed = [('idle', 'file-ready'), ('confirming', 'encrypting')]
        result   = self.utils.coverage(self.upload, observed)
        assert result['covered'] == 2
        assert result['covered'] < result['total']
        assert 0 < result['coverage_pct'] < 100

    # --------------------------------------------------------- security_annotations

    def test__upload_security_annotations(self):
        tagged = self.utils.security_annotations(self.upload)
        assert len(tagged) >= 2
        tags = {str(t.security) for t in tagged}
        assert 'plaintext_in_memory' in tags

    def test__download_security_annotations(self):
        tagged = self.utils.security_annotations(self.download)
        tags   = {str(t.security) for t in tagged}
        assert 'key_in_memory'    in tags
        assert 'plaintext_in_dom' in tags
