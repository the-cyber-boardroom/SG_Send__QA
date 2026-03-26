# ═══════════════════════════════════════════════════════════════════════════════
# Layer 2: Upload feature operations
# Each endpoint runs a complete upload workflow and returns the result.
# ═══════════════════════════════════════════════════════════════════════════════
import base64
from fastapi                            import APIRouter, Body
from sg_send_qa.api.QA_API__Runner      import QA_API__Runner
from sg_send_qa.api.Schema__QA_Request  import Schema__QA_Request

router = APIRouter(prefix="/api/upload", tags=["upload"])


def _req(body: dict) -> Schema__QA_Request:
    return Schema__QA_Request(**{k: v for k, v in body.items()
                                 if k in Schema__QA_Request.__annotations__})

def _file_bytes(body: dict) -> bytes:                           # decode base64 content, or use default test payload
    content = body.get('content', '')
    if content:
        return base64.b64decode(content)
    return b'Hello from SG/Send QA API'


@router.post("/combined")
def upload_combined(body: dict = Body(default={})):
    req      = _req(body)
    filename = body.get('filename', 'qa-test.txt')
    def workflow(session):
        link = session.sg_send.workflow__upload_combined(
            token         = session.access_token  ,
            filename      = filename              ,
            content_bytes = _file_bytes(body)     ,
        )
        model = session.sg_send.extract__upload_page()
        return {
            "link"         : link           ,
            "upload_state" : model.state    ,
            "page_model"   : model.json()   ,
        }
    return QA_API__Runner(request=req).run(workflow)


@router.post("/friendly_token")
def upload_friendly_token(body: dict = Body(default={})):
    req      = _req(body)
    filename = body.get('filename', 'qa-test.txt')
    def workflow(session):
        token = session.sg_send.workflow__upload_friendly_token(
            token         = session.access_token  ,
            filename      = filename              ,
            content_bytes = _file_bytes(body)     ,
        )
        model = session.sg_send.extract__upload_page()
        return {
            "token"        : token          ,
            "upload_state" : model.state    ,
            "page_model"   : model.json()   ,
        }
    return QA_API__Runner(request=req).run(workflow)


@router.post("/separate_key")
def upload_separate_key(body: dict = Body(default={})):
    req      = _req(body)
    filename = body.get('filename', 'qa-test.txt')
    def workflow(session):
        link, key = session.sg_send.workflow__upload_separate_key(
            token         = session.access_token  ,
            filename      = filename              ,
            content_bytes = _file_bytes(body)     ,
        )
        model = session.sg_send.extract__upload_page()
        return {
            "link"         : link           ,
            "key"          : key            ,
            "upload_state" : model.state    ,
            "page_model"   : model.json()   ,
        }
    return QA_API__Runner(request=req).run(workflow)
