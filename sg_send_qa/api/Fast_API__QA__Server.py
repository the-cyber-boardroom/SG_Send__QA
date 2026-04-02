# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__QA__Server — unified QA API server
#
# Extends Serverless__Fast_API for Lambda + local dev + TestClient support.
#
# Entry points:
#   from sg_send_qa.api.Fast_API__QA__Server import Fast_API__QA__Server
#
# Lambda handler:
#   fast_api = Fast_API__QA__Server().setup()
#   handler  = fast_api.handler()
#   app      = fast_api.app()
#   def run(event, context=None):
#       return handler(event, context)
#
# Local dev / test:
#   fast_api = Fast_API__QA__Server().setup()
#   client   = fast_api.client()   # Starlette TestClient — no HTTP
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API        import Serverless__Fast_API
from osbot_fast_api_serverless.fast_api.routes.Routes__Info         import Routes__Info
from sg_send_qa.api.QA_API__Runner                                  import QA_API__Runner
from sg_send_qa.api.routes.routes__browser                          import Routes__Browser
from sg_send_qa.api.routes.routes__upload                           import Routes__Upload
from sg_send_qa.api.routes.routes__download                         import Routes__Download
from sg_send_qa.api.routes.routes__workflow                         import Routes__Workflow
from sg_send_qa.utils.Version                                       import version__sg_send__qa

# [LIB-2026-04-01-003] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
class Fast_API__QA__Server(Serverless__Fast_API):

    qa_runner : QA_API__Runner = None                           # injected or auto-created in setup()

    def setup(self):
        with self.config as _:
            _.name           = 'SG/Send QA API'
            _.version        = version__sg_send__qa
            _.description    = 'Browser automation API for SG/Send QA'
            _.enable_api_key = False                            # internal tooling — per-route auth added later if needed

        if self.qa_runner is None:                              # if-None guard: allows test injection
            self.qa_runner = QA_API__Runner()

        return super().setup()

    def setup_routes(self):
        self.add_routes(Routes__Info    )
        self.add_routes(Routes__Browser , qa_runner=self.qa_runner)
        self.add_routes(Routes__Upload  , qa_runner=self.qa_runner)
        self.add_routes(Routes__Download, qa_runner=self.qa_runner)
        self.add_routes(Routes__Workflow, qa_runner=self.qa_runner)
        return self


# ── Module-level singletons ────────────────────────────────────────────────────
# Exposed so uvicorn can reference them directly:
#   uvicorn sg_send_qa.api.Fast_API__QA__Server:app --reload
#
# Also the Lambda handler:
#   HANDLER=sg_send_qa.api.Fast_API__QA__Server.run
# ──────────────────────────────────────────────────────────────────────────────
_fast_api = Fast_API__QA__Server().setup()

# [LIB-2026-04-01-004] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
handler   = _fast_api.handler()         # Mangum-wrapped ASGI — for Lambda direct invoke
app       = _fast_api.app()             # raw ASGI app — for uvicorn / Lambda Web Adapter


def run(event, context=None):           # Lambda entry point
    return handler(event, context)
