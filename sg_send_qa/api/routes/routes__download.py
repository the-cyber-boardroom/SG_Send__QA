# ═══════════════════════════════════════════════════════════════════════════════
# Layer 2: Download feature operations
# ═══════════════════════════════════════════════════════════════════════════════
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from sg_send_qa.api.QA_API__Runner              import QA_API__Runner
from sg_send_qa.api.Schema__QA_Request          import Schema__QA_Request


class Routes__Download(Fast_API__Routes):
    tag       : str            = 'download'
    qa_runner : QA_API__Runner

    def browse(self, body: Schema__QA_Request) -> dict:         # POST /download/browse
        def workflow(session):
            transfer_id = (body.options or {}).get('transfer_id', '')
            key         = (body.options or {}).get('key', '')
            session.sg_send.page__browse_with_hash(transfer_id, key)
            session.sg_send.wait_for_download_states(["complete", "error"])
            model = session.sg_send.extract__browse_page()
            return {
                "download_state" : model.state       ,
                "content_text"   : model.content_text,
                "page_model"     : model.json()      ,
            }
        return self.qa_runner.run(body, workflow)

    def friendly_token(self, body: Schema__QA_Request) -> dict:   # POST /download/friendly_token
        def workflow(session):
            token = (body.options or {}).get('token', '')
            session.sg_send.page__welcome()
            session.sg_send.download__enter_manual_id(token)
            session.sg_send.download__submit_manual_entry()
            session.sg_send.wait_for_download_states(["complete", "error"])
            model = session.sg_send.extract__download_page()
            return {
                "download_state" : model.state       ,
                "content_text"   : model.content_text,
                "page_model"     : model.json()      ,
            }
        return self.qa_runner.run(body, workflow)

    def separate_key(self, body: Schema__QA_Request) -> dict:   # POST /download/separate_key
        def workflow(session):
            transfer_id = (body.options or {}).get('transfer_id', '')
            key         = (body.options or {}).get('key', '')
            session.sg_send.page__download_with_id(transfer_id)
            session.sg_send.wait_for_download_state("ready")
            session.sg_send.download__enter_key(key)
            session.sg_send.download__click_decrypt()
            model = session.sg_send.extract__download_page()
            return {
                "download_state" : model.state       ,
                "content_text"   : model.content_text,
                "page_model"     : model.json()      ,
            }
        return self.qa_runner.run(body, workflow)

    def setup_routes(self):
        self.add_route_post(self.browse        )
        self.add_route_post(self.friendly_token)
        self.add_route_post(self.separate_key  )
        return self
