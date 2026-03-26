# ═══════════════════════════════════════════════════════════════════════════════
# Layer 2: Download feature operations
# ═══════════════════════════════════════════════════════════════════════════════
from fastapi                            import APIRouter, Body
from sg_send_qa.api.QA_API__Runner      import QA_API__Runner
from sg_send_qa.api.Schema__QA_Request  import Schema__QA_Request

router = APIRouter(prefix="/api/download", tags=["download"])


def _req(body: dict) -> Schema__QA_Request:
    return Schema__QA_Request(**{k: v for k, v in body.items()
                                 if k in Schema__QA_Request.__annotations__})


@router.post("/browse")
def download_browse(body: dict = Body(default={})):
    req         = _req(body)
    transfer_id = body.get('transfer_id', '')
    key         = body.get('key', '')
    def workflow(session):
        session.sg_send.page__browse_with_hash(transfer_id, key)
        session.sg_send.wait_for_download_states(["complete", "error"])
        model = session.sg_send.extract__browse_page()
        return {
            "download_state" : model.state        ,
            "content_text"   : model.content_text ,
            "page_model"     : model.json()        ,
        }
    return QA_API__Runner(request=req).run(workflow)


@router.post("/friendly_token")
def download_friendly_token(body: dict = Body(default={})):
    req   = _req(body)
    token = body.get('token', '')
    def workflow(session):
        session.sg_send.page__welcome()
        session.sg_send.download__enter_manual_id(token)
        session.sg_send.download__submit_manual_entry()
        session.sg_send.wait_for_download_states(["complete", "error"])
        model = session.sg_send.extract__download_page()
        return {
            "download_state" : model.state        ,
            "content_text"   : model.content_text ,
            "page_model"     : model.json()        ,
        }
    return QA_API__Runner(request=req).run(workflow)


@router.post("/separate_key")
def download_separate_key(body: dict = Body(default={})):
    req         = _req(body)
    transfer_id = body.get('transfer_id', '')
    key         = body.get('key', '')
    def workflow(session):
        session.sg_send.page__download_with_id(transfer_id)
        session.sg_send.wait_for_download_state("ready")
        session.sg_send.download__enter_key(key)
        session.sg_send.download__click_decrypt()
        model = session.sg_send.extract__download_page()
        return {
            "download_state" : model.state        ,
            "content_text"   : model.content_text ,
            "page_model"     : model.json()        ,
        }
    return QA_API__Runner(request=req).run(workflow)
