# ═══════════════════════════════════════════════════════════════════════════════
# Layer 0: Raw browser actions
# Every route is POST, stateless, returns JSON.
# ═══════════════════════════════════════════════════════════════════════════════
import base64
import tempfile
import os
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from sg_send_qa.api.QA_API__Runner              import QA_API__Runner
from sg_send_qa.api.Schema__QA_Request          import Schema__QA_Request


class Routes__Browser(Fast_API__Routes):
    tag       : str           = 'browser'
    qa_runner : QA_API__Runner

    def open(self, body: Schema__QA_Request) -> dict:           # POST /browser/open — navigate to a page, return url+title
        def workflow(session):
            page = (body.options or {}).get('page', '')
            if page:
                session.sg_send.open(page)
            else:
                session.sg_send.page__root()
            return {
                "url"        : session.sg_send.url()  ,
                "title"      : session.sg_send.title(),
                "data_ready" : True                   ,
            }
        return self.qa_runner.run(body, workflow)

    def screenshot(self, body: Schema__QA_Request) -> dict:     # POST /browser/screenshot — navigate and capture PNG (base64)
        def workflow(session):
            page = (body.options or {}).get('page', '')
            if page:
                session.sg_send.open(page)
            else:
                session.sg_send.page__root()
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                tmp = f.name
            try:
                session.sg_send.raw_page().screenshot(path=tmp, full_page=False)
                png_b64 = base64.b64encode(open(tmp, 'rb').read()).decode()
            finally:
                os.unlink(tmp)
            return {
                "url"         : session.sg_send.url(),
                "screenshots" : [png_b64]             ,
            }
        return self.qa_runner.run(body, workflow)

    def setup_routes(self):
        self.add_route_post(self.open      )
        self.add_route_post(self.screenshot)
        return self
