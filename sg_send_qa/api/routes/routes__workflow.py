# ═══════════════════════════════════════════════════════════════════════════════
# Layer 3: User story workflows — full persona replays
# Each endpoint runs a complete user journey, fully self-contained.
# ═══════════════════════════════════════════════════════════════════════════════
import base64
from urllib.parse                               import urlparse
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from sg_send_qa.api.QA_API__Runner              import QA_API__Runner
from sg_send_qa.api.Schema__Upload_Request      import Schema__Upload_Request


class Routes__Workflow(Fast_API__Routes):
    tag       : str            = 'workflow'
    qa_runner : QA_API__Runner

    def persona_ab__send_and_receive(self, body: Schema__Upload_Request) -> dict:
        """Persona A (sender) + Persona B (receiver): upload a file, open the link, verify content."""
        def workflow(session):
            content  = base64.b64decode(body.content) if body.content else b'Hello from SG/Send QA API'
            expected = content.decode('utf-8', errors='replace')

            # ── Persona A: upload ──────────────────────────────────────────
            if body.share_mode == 'combined':
                link = session.sg_send.workflow__upload_combined(
                    token=session.access_token, filename=body.filename, content_bytes=content)
                send_result = {"share_mode": "combined", "link": link}
            elif body.share_mode == 'token':
                token = session.sg_send.workflow__upload_friendly_token(
                    token=session.access_token, filename=body.filename, content_bytes=content)
                send_result = {"share_mode": "token", "friendly_token": token}
            else:
                raise ValueError(f"Unsupported share_mode: {body.share_mode!r}")

            # ── Persona B: receive ─────────────────────────────────────────
            if body.share_mode == 'combined':
                parsed      = urlparse(link)
                fragment    = parsed.fragment                   # 'transfer_id/key_b64'
                parts       = fragment.split('/', 1)
                transfer_id = parts[0] if parts else ''
                key_b64     = parts[1] if len(parts) > 1 else ''
                session.sg_send.page__browse_with_hash(transfer_id, key_b64)
                session.sg_send.wait_for_download_states(["complete", "error"])
                model          = session.sg_send.extract__browse_page()
                content_text   = model.content_text
                download_state = model.state
            else:
                raise ValueError(f"Receive not yet implemented for share_mode: {body.share_mode!r}")

            content_matches = expected.strip() in content_text if content_text else False
            return {
                "send_result"    : send_result    ,
                "download_state" : download_state ,
                "content_text"   : content_text   ,
                "content_matches": content_matches,
            }
        return self.qa_runner.run(body, workflow)

    def setup_routes(self):
        self.add_route_post(self.persona_ab__send_and_receive)
        return self
