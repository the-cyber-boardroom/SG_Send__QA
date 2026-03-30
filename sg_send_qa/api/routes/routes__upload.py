# ═══════════════════════════════════════════════════════════════════════════════
# Layer 2: Upload feature operations
# Each endpoint runs a complete upload workflow and returns the result.
# ═══════════════════════════════════════════════════════════════════════════════
import base64
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from sg_send_qa.api.QA_API__Runner              import QA_API__Runner
from sg_send_qa.api.Schema__Upload_Request      import Schema__Upload_Request


def _file_bytes(body: Schema__Upload_Request) -> bytes:         # decode base64 content, or use default test payload
    if body.content:
        return base64.b64decode(body.content)
    return b'Hello from SG/Send QA API'


class Routes__Upload(Fast_API__Routes):
    tag       : str            = 'upload'
    qa_runner : QA_API__Runner

    def combined(self, body: Schema__Upload_Request) -> dict:   # POST /upload/combined
        def workflow(session):
            link = session.sg_send.workflow__upload_combined(
                token         = session.access_token,
                filename      = body.filename       ,
                content_bytes = _file_bytes(body)   ,
            )
            model = session.sg_send.extract__upload_page()
            return {
                "link"         : link        ,
                "upload_state" : model.state ,
                "page_model"   : model.json(),
            }
        return self.qa_runner.run(body, workflow)

    def friendly_token(self, body: Schema__Upload_Request) -> dict:   # POST /upload/friendly_token
        def workflow(session):
            token = session.sg_send.workflow__upload_friendly_token(
                token         = session.access_token,
                filename      = body.filename       ,
                content_bytes = _file_bytes(body)   ,
            )
            model = session.sg_send.extract__upload_page()
            return {
                "token"        : token       ,
                "upload_state" : model.state ,
                "page_model"   : model.json(),
            }
        return self.qa_runner.run(body, workflow)

    def separate_key(self, body: Schema__Upload_Request) -> dict:   # POST /upload/separate_key
        def workflow(session):
            link, key = session.sg_send.workflow__upload_separate_key(
                token         = session.access_token,
                filename      = body.filename       ,
                content_bytes = _file_bytes(body)   ,
            )
            model = session.sg_send.extract__upload_page()
            return {
                "link"         : link        ,
                "key"          : key         ,
                "upload_state" : model.state ,
                "page_model"   : model.json(),
            }
        return self.qa_runner.run(body, workflow)

    def setup_routes(self):
        self.add_route_post(self.combined      )
        self.add_route_post(self.friendly_token)
        self.add_route_post(self.separate_key  )
        return self
