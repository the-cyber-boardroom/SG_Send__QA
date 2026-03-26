# ═══════════════════════════════════════════════════════════════════════════════
# QA_API__Runner — execution engine for all QA API requests
#
# Single entry point for all workflows. Handles:
#   - trace ID generation
#   - capture config defaults
#   - session lifecycle (create → execute → teardown)
#   - timing
#   - error handling → fail response
# ═══════════════════════════════════════════════════════════════════════════════
import time
import uuid
from osbot_utils.type_safe.Type_Safe        import Type_Safe
from sg_send_qa.api.Schema__QA_Request      import Schema__QA_Request
from sg_send_qa.api.Schema__QA_Response     import Schema__QA_Response
from sg_send_qa.api.Schema__Capture_Config  import Schema__Capture_Config
from sg_send_qa.api.QA_API__Session         import QA_API__Session


class QA_API__Runner(Type_Safe):

    def _ensure_capture(self, request: Schema__QA_Request):     # populate capture config defaults based on mode if not provided
        if request.capture is None:
            request.capture = Schema__Capture_Config()
            if request.mode == 'qa':                            # qa mode: enable screenshots
                request.capture.screenshots = True

    def _ensure_trace_id(self, request: Schema__QA_Request):    # auto-generate trace ID if caller didn't provide one
        if not request.trace_id:
            request.trace_id = uuid.uuid4().hex[:8]

    def run(self, request: Schema__QA_Request, workflow_fn) -> dict:    # execute a workflow function inside a managed session
        self._ensure_capture(request)
        self._ensure_trace_id(request)
        start    = time.time()
        response = Schema__QA_Response(trace_id=request.trace_id)
        try:
            with QA_API__Session(request=request) as session:
                result                        = workflow_fn(session)
                response.status               = 'pass'
                response.duration_ms          = int((time.time() - start) * 1000)
                response.transitions_observed = session.transitions_observed
                return {**response.json(), **result}
        except Exception as exc:
            response.status      = 'fail'
            response.error       = str(exc)
            response.duration_ms = int((time.time() - start) * 1000)
            return response.json()
