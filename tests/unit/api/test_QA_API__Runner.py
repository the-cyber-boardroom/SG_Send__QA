from unittest                               import TestCase
from sg_send_qa.api.QA_API__Runner          import QA_API__Runner
from sg_send_qa.api.Schema__QA_Request      import Schema__QA_Request
from sg_send_qa.api.Schema__Capture_Config  import Schema__Capture_Config


class test_QA_API__Runner(TestCase):

    def test__ensure_trace_id__generates_when_empty(self):
        runner = QA_API__Runner(request=Schema__QA_Request())
        assert runner.request.trace_id == ''
        runner._ensure_trace_id()
        assert len(runner.request.trace_id) == 8
        assert runner.request.trace_id.isalnum()

    def test__ensure_trace_id__preserves_existing(self):
        runner = QA_API__Runner(request=Schema__QA_Request(trace_id='my-trace'))
        runner._ensure_trace_id()
        assert runner.request.trace_id == 'my-trace'

    def test__ensure_capture__sets_defaults_for_smoke(self):
        runner = QA_API__Runner(request=Schema__QA_Request(mode='smoke'))
        runner._ensure_capture()
        assert isinstance(runner.request.capture, Schema__Capture_Config)
        assert runner.request.capture.screenshots is False     # smoke: no screenshots by default

    def test__ensure_capture__enables_screenshots_for_qa(self):
        runner = QA_API__Runner(request=Schema__QA_Request(mode='qa'))
        runner._ensure_capture()
        assert runner.request.capture.screenshots is True      # qa mode: screenshots on

    def test__ensure_capture__preserves_existing_config(self):
        config = Schema__Capture_Config(screenshots=True)
        runner = QA_API__Runner(request=Schema__QA_Request(capture=config))
        runner._ensure_capture()
        assert runner.request.capture.screenshots is True      # pre-set value preserved

    def test__run__returns_fail_on_exception(self):
        runner = QA_API__Runner(request=Schema__QA_Request())

        def bad_workflow(session):
            raise ValueError("something went wrong")

        # patch session to avoid starting a real browser
        import unittest.mock as mock
        with mock.patch('sg_send_qa.api.QA_API__Runner.QA_API__Session') as MockSession:
            MockSession.return_value.__enter__.side_effect = ValueError("something went wrong")
            MockSession.return_value.__exit__ = mock.MagicMock(return_value=False)
            result = runner.run(bad_workflow)

        assert result['status']     == 'fail'
        assert 'something went wrong' in result['error']
        assert result['duration_ms'] >= 0
        assert len(result['trace_id']) == 8

    def test__run__returns_pass_on_success(self):
        runner = QA_API__Runner(request=Schema__QA_Request())

        def good_workflow(session):
            return {"link": "http://localhost/#id/key"}

        import unittest.mock as mock
        mock_session = mock.MagicMock()
        with mock.patch('sg_send_qa.api.QA_API__Runner.QA_API__Session') as MockSession:
            MockSession.return_value.__enter__.return_value = mock_session
            MockSession.return_value.__exit__ = mock.MagicMock(return_value=False)
            result = runner.run(good_workflow)

        assert result['status']            == 'pass'
        assert result['link']              == 'http://localhost/#id/key'
        assert result['duration_ms']       >= 0
