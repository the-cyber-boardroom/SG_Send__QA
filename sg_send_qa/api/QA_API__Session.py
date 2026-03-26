# ═══════════════════════════════════════════════════════════════════════════════
# QA_API__Session — browser session lifecycle for a single API request
#
# Each request gets a fresh session: browser + servers (local) or browser only
# (live). Nothing survives between requests. Lambda-compatible by design.
# ═══════════════════════════════════════════════════════════════════════════════
from typing                                         import List
from osbot_utils.type_safe.Type_Safe                import Type_Safe
from sg_send_qa.api.Schema__QA_Request              import Schema__QA_Request
from sg_send_qa.api.Schema__Transition_Observed     import Schema__Transition_Observed


class QA_API__Session(Type_Safe):
    request              : Schema__QA_Request             = None

    harness              : object                         = None  # SG_Send__Browser__Test_Harness (local mode only)
    sg_send              : object                         = None  # SG_Send__Browser__Pages
    access_token         : str                            = ''
    transitions_observed : List[Schema__Transition_Observed]      # UI transitions recorded during workflow

    def record_transition(self, from_state: str, to_state: str, trigger: str = '') -> None:
        """Record a UI state transition observed during workflow execution."""
        self.transitions_observed.append(
            Schema__Transition_Observed(from_state=from_state, to_state=to_state, trigger=trigger)
        )

    def __enter__(self):
        if self.request.target == 'local':
            self._setup_local()
        else:
            self._setup_live()
        if self.request.trace_id:                               # propagate trace ID to all browser requests
            self.sg_send.raw_page().set_extra_http_headers(
                {'X-QA-Trace-ID': self.request.trace_id}
            )
        return self

    def __exit__(self, *args):
        if self.harness:
            self.harness.teardown()

    def _setup_local(self):
        from sg_send_qa.browser.SG_Send__Browser__Test_Harness import SG_Send__Browser__Test_Harness
        self.harness      = SG_Send__Browser__Test_Harness().headless(True).setup()
        self.sg_send      = self.harness.sg_send
        self.access_token = self.harness.access_token()
        self.harness.set_access_token()

    def _setup_live(self):                                      # live mode: browser pointed at caller-supplied URL
        from sg_send_qa.browser.SG_Send__Browser__Pages import SG_Send__Browser__Pages
        self.sg_send      = SG_Send__Browser__Pages(headless=True,
                                                    target_server=self.request.target)
        self.access_token = self.request.access_token
        if self.access_token:
            self.sg_send.page__qa_setup()
            self.sg_send.storage__set_token(self.access_token)
