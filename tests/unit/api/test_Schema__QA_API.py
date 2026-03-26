from unittest                                   import TestCase
from sg_send_qa.api.Schema__Capture_Config      import Schema__Capture_Config
from sg_send_qa.api.Schema__QA_Request          import Schema__QA_Request
from sg_send_qa.api.Schema__QA_Response         import Schema__QA_Response
from sg_send_qa.api.Schema__Transition_Observed import Schema__Transition_Observed


class test_Schema__Capture_Config(TestCase):

    def setUp(self):
        self.schema = Schema__Capture_Config()

    def test__defaults(self):
        assert self.schema.execution_result   is True
        assert self.schema.page_model         is True
        assert self.schema.screenshots        is False
        assert self.schema.screenshot_on_fail is True
        assert self.schema.video              is False
        assert self.schema.pdf                is False
        assert self.schema.browser_console    is False
        assert self.schema.browser_trace      is False
        assert self.schema.python_console     is False
        assert self.schema.python_trace       is False
        assert self.schema.performance_data   is True
        assert self.schema.prometheus         is True
        assert self.schema.network_log        is False

    def test__field_count(self):
        assert len(self.schema.json()) == 13                    # 13 capture flags

    def test__json_roundtrip(self):
        self.schema.screenshots = True
        data = self.schema.json()
        assert data['screenshots'] is True
        restored = Schema__Capture_Config(**data)
        assert restored.screenshots is True


class test_Schema__QA_Request(TestCase):

    def setUp(self):
        self.schema = Schema__QA_Request()

    def test__defaults(self):
        assert self.schema.target       == 'local'
        assert self.schema.access_token == ''
        assert self.schema.mode         == 'smoke'
        assert self.schema.trace_id     == ''
        assert self.schema.capture      is None
        assert self.schema.options      is None

    def test__capture_field_accepts_config(self):
        self.schema.capture = Schema__Capture_Config()
        assert isinstance(self.schema.capture, Schema__Capture_Config)
        assert self.schema.capture.execution_result is True

    def test__live_target(self):
        req = Schema__QA_Request(target='https://send.sgraph.ai', access_token='tok-123')
        assert req.target       == 'https://send.sgraph.ai'
        assert req.access_token == 'tok-123'


class test_Schema__QA_Response(TestCase):

    def setUp(self):
        self.schema = Schema__QA_Response()

    def test__defaults(self):
        assert self.schema.status      == ''
        assert self.schema.trace_id    == ''
        assert self.schema.duration_ms == 0
        assert self.schema.error       == ''

    def test__pass_response(self):
        resp = Schema__QA_Response(status='pass', trace_id='abc-123', duration_ms=3200)
        assert resp.status      == 'pass'
        assert resp.trace_id    == 'abc-123'
        assert resp.duration_ms == 3200

    def test__fail_response(self):
        resp = Schema__QA_Response(status='fail', error='TimeoutError: upload did not complete')
        assert resp.status == 'fail'
        assert 'TimeoutError' in resp.error

    def test__json_roundtrip(self):
        resp = Schema__QA_Response(status='pass', duration_ms=1500)
        data = resp.json()
        assert data['status']      == 'pass'
        assert data['duration_ms'] == 1500

    def test__transitions_observed_defaults_empty(self):
        assert list(self.schema.transitions_observed) == []

    def test__transitions_observed_accepts_list(self):
        t = Schema__Transition_Observed(from_state='idle', to_state='file-ready', trigger='file_selected')
        self.schema.transitions_observed.append(t)
        assert len(self.schema.transitions_observed) == 1
        assert self.schema.transitions_observed[0].from_state == 'idle'

    def test__transitions_observed_in_json(self):
        resp = Schema__QA_Response(status='pass')
        resp.transitions_observed.append(
            Schema__Transition_Observed(from_state='idle', to_state='file-ready', trigger='file_selected')
        )
        data = resp.json()
        assert 'transitions_observed' in data
        assert data['transitions_observed'][0]['to_state'] == 'file-ready'
