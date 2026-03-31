# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Test_Objs__QA — singleton test harness for QA API unit tests
#
# Usage:
#   from sg_send_qa.api.test_utils.Fast_API__Test_Objs__QA import setup__qa_fast_api_test_objs
#
#   def test_health():
#       objs     = setup__qa_fast_api_test_objs()
#       response = objs.fast_api__client.get('/info/health')
#       assert response.status_code == 200
#
# Inject a custom runner for tests that must not start Playwright:
#   objs = setup__qa_fast_api_test_objs(qa_runner=stub_runner)
# ═══════════════════════════════════════════════════════════════════════════════
from fastapi                                import FastAPI
from fastapi.testclient                     import TestClient
from osbot_utils.type_safe.Type_Safe        import Type_Safe
from sg_send_qa.api.Fast_API__QA__Server    import Fast_API__QA__Server
from sg_send_qa.api.QA_API__Runner          import QA_API__Runner

# todo: add tests that use this classes
#       since at the moment there doesn't seem to be any
class Fast_API__Test_Objs__QA(Type_Safe):
    fast_api        : Fast_API__QA__Server = None
    fast_api__app   : FastAPI              = None
    fast_api__client: TestClient           = None


_test_singleton = None


def setup__qa_fast_api_test_objs(qa_runner: QA_API__Runner = None) -> Fast_API__Test_Objs__QA:
    global _test_singleton
    if _test_singleton is None:
        kwargs   = dict(qa_runner=qa_runner) if qa_runner is not None else {}
        fast_api = Fast_API__QA__Server(**kwargs).setup()
        _test_singleton = Fast_API__Test_Objs__QA(
            fast_api         = fast_api         ,
            fast_api__app    = fast_api.app()   ,
            fast_api__client = fast_api.client(),
        )
    return _test_singleton
