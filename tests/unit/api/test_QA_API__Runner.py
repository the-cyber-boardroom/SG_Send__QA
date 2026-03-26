from unittest                               import TestCase
from sg_send_qa.api.QA_API__Runner          import QA_API__Runner
from sg_send_qa.api.QA_API__Session         import QA_API__Session
from sg_send_qa.api.Schema__QA_Request      import Schema__QA_Request
from sg_send_qa.api.Schema__Capture_Config  import Schema__Capture_Config


class test_QA_API__Runner(TestCase):

    def test__ensure_trace_id__generates_when_empty(self):
        runner  = QA_API__Runner()
        request = Schema__QA_Request()
        assert request.trace_id == ''
        runner._ensure_trace_id(request)
        assert len(request.trace_id) == 8
        assert request.trace_id.isalnum()

    def test__ensure_trace_id__preserves_existing(self):
        runner  = QA_API__Runner()
        request = Schema__QA_Request(trace_id='my-trace')
        runner._ensure_trace_id(request)
        assert request.trace_id == 'my-trace'

    def test__ensure_capture__sets_defaults_for_smoke(self):
        runner  = QA_API__Runner()
        request = Schema__QA_Request(mode='smoke')
        runner._ensure_capture(request)
        assert isinstance(request.capture, Schema__Capture_Config)
        assert request.capture.screenshots is False         # smoke: no screenshots by default

    def test__ensure_capture__enables_screenshots_for_qa(self):
        runner  = QA_API__Runner()
        request = Schema__QA_Request(mode='qa')
        runner._ensure_capture(request)
        assert request.capture.screenshots is True          # qa mode: screenshots on

    def test__ensure_capture__preserves_existing_config(self):
        config  = Schema__Capture_Config(screenshots=True)
        runner  = QA_API__Runner()
        request = Schema__QA_Request(capture=config)
        runner._ensure_capture(request)
        assert request.capture.screenshots is True          # pre-set value preserved

    def test__run__returns_fail_on_exception(self):
        runner  = QA_API__Runner()
        request = Schema__QA_Request()

        def bad_workflow(session):
            raise ValueError("something went wrong")

        import unittest.mock as mock
        with mock.patch('sg_send_qa.api.QA_API__Runner.QA_API__Session') as MockSession:
            MockSession.return_value.__enter__.side_effect = ValueError("something went wrong")
            MockSession.return_value.__exit__ = mock.MagicMock(return_value=False)
            result = runner.run(request, bad_workflow)

        assert result['status']              == 'fail'
        assert 'something went wrong' in result['error']
        assert result['duration_ms']         >= 0
        assert len(result['trace_id'])       == 8

    def test__run__returns_pass_on_success(self):
        runner       = QA_API__Runner()
        request      = Schema__QA_Request()
        real_session = QA_API__Session(request=request)

        def good_workflow(session):
            return {"link": "http://localhost/#id/key"}

        import unittest.mock as mock
        with mock.patch('sg_send_qa.api.QA_API__Runner.QA_API__Session') as MockSession:
            MockSession.return_value.__enter__.return_value = real_session
            MockSession.return_value.__exit__ = mock.MagicMock(return_value=False)
            result = runner.run(request, good_workflow)

        assert result['status']        == 'pass'
        assert result['link']          == 'http://localhost/#id/key'
        assert result['duration_ms']   >= 0

    def test__run__merges_transitions_observed(self):
        """Transitions recorded in session appear in response as serialised dicts."""
        runner       = QA_API__Runner()
        request      = Schema__QA_Request()
        real_session = QA_API__Session(request=request)

        def workflow_with_transitions(session):
            session.record_transition('idle',       'file-ready',     'file_selected')
            session.record_transition('file-ready', 'choosing-share', 'single_file')
            return {}

        import unittest.mock as mock
        with mock.patch('sg_send_qa.api.QA_API__Runner.QA_API__Session') as MockSession:
            MockSession.return_value.__enter__.return_value = real_session
            MockSession.return_value.__exit__ = mock.MagicMock(return_value=False)
            result = runner.run(request, workflow_with_transitions)

        assert result['status'] == 'pass'
        assert len(result['transitions_observed']) == 2
        assert result['transitions_observed'][0]['from_state'] == 'idle'
        assert result['transitions_observed'][1]['to_state']   == 'choosing-share'

    def test__run__transitions_empty_by_default(self):
        """If workflow doesn't record transitions, list is empty."""
        runner       = QA_API__Runner()
        request      = Schema__QA_Request()
        real_session = QA_API__Session(request=request)

        def no_transitions(session):
            return {}

        import unittest.mock as mock
        with mock.patch('sg_send_qa.api.QA_API__Runner.QA_API__Session') as MockSession:
            MockSession.return_value.__enter__.return_value = real_session
            MockSession.return_value.__exit__ = mock.MagicMock(return_value=False)
            result = runner.run(request, no_transitions)

        assert result['status']               == 'pass'
        assert result['transitions_observed'] == []
