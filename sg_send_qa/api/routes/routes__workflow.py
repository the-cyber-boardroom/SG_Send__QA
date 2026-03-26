# ═══════════════════════════════════════════════════════════════════════════════
# Layer 3: User story workflows — full persona replays
# Each endpoint runs a complete user journey, fully self-contained.
# ═══════════════════════════════════════════════════════════════════════════════
import base64
from fastapi                            import APIRouter, Body
from sg_send_qa.api.QA_API__Runner      import QA_API__Runner
from sg_send_qa.api.Schema__QA_Request  import Schema__QA_Request

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


def _req(body: dict) -> Schema__QA_Request:
    return Schema__QA_Request(**{k: v for k, v in body.items()
                                 if k in Schema__QA_Request.__annotations__})

def _file_bytes(body: dict) -> bytes:
    content = body.get('content', '')
    return base64.b64decode(content) if content else b'Hello from SG/Send QA API'


@router.post("/persona_ab__send_and_receive")
def persona_ab__send_and_receive(body: dict = Body(default={})):
    """Persona A (sender) + Persona B (receiver): upload a file, open the link, verify content."""
    req        = _req(body)
    filename   = body.get('filename', 'qa-test.txt')
    share_mode = body.get('share_mode', 'combined')
    content    = _file_bytes(body)
    expected   = content.decode('utf-8', errors='replace')

    def workflow(session):
        # ── Persona A: upload ──────────────────────────────────────────
        if share_mode == 'combined':
            link = session.sg_send.workflow__upload_combined(
                token=session.access_token, filename=filename, content_bytes=content)
            send_result = {"share_mode": "combined", "link": link}
        elif share_mode == 'token':
            token = session.sg_send.workflow__upload_friendly_token(
                token=session.access_token, filename=filename, content_bytes=content)
            send_result = {"share_mode": "token", "friendly_token": token}
        else:
            raise ValueError(f"Unsupported share_mode: {share_mode!r}")

        # ── Persona B: receive ─────────────────────────────────────────
        if share_mode == 'combined':
            from urllib.parse import urlparse
            parsed      = urlparse(link)
            fragment    = parsed.fragment                       # 'transfer_id/key_b64'
            parts       = fragment.split('/', 1)
            transfer_id = parts[0] if parts else ''
            key_b64     = parts[1] if len(parts) > 1 else ''
            session.sg_send.page__browse_with_hash(transfer_id, key_b64)
            session.sg_send.wait_for_download_states(["complete", "error"])
            model          = session.sg_send.extract__browse_page()
            content_text   = model.content_text
            download_state = model.state
        else:
            raise ValueError(f"Receive not yet implemented for share_mode: {share_mode!r}")

        content_matches = expected.strip() in content_text if content_text else False
        return {
            "send_result"    : send_result    ,
            "download_state" : download_state ,
            "content_text"   : content_text   ,
            "content_matches": content_matches,
        }
    return QA_API__Runner(request=req).run(workflow)
