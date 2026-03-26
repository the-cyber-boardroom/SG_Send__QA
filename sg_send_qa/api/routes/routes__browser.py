# ═══════════════════════════════════════════════════════════════════════════════
# Layer 0: Raw browser actions
# Every route is POST, stateless, returns JSON.
# Request bodies are plain dicts — converted to Schema__QA_Request internally.
# ═══════════════════════════════════════════════════════════════════════════════
from fastapi                            import APIRouter
from fastapi                            import Body
from sg_send_qa.api.QA_API__Runner      import QA_API__Runner
from sg_send_qa.api.Schema__QA_Request  import Schema__QA_Request

router = APIRouter(prefix="/api/browser", tags=["browser"])


def _req(body: dict) -> Schema__QA_Request:                     # build request schema from raw dict
    return Schema__QA_Request(**{k: v for k, v in body.items()
                                 if k in Schema__QA_Request.__annotations__})


@router.post("/open")
def browser_open(body: dict = Body(default={})):
    req  = _req(body)
    page = body.get('page', '')
    def workflow(session):
        if page:
            session.sg_send.open(page)
        else:
            session.sg_send.page__root()
        return {
            "url"        : session.sg_send.url()  ,
            "title"      : session.sg_send.title(),
            "data_ready" : True                   ,
        }
    return QA_API__Runner(request=req).run(workflow)


@router.post("/screenshot")
def browser_screenshot(body: dict = Body(default={})):
    import base64, tempfile, os
    req  = _req(body)
    page = body.get('page', '')
    def workflow(session):
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
    return QA_API__Runner(request=req).run(workflow)
