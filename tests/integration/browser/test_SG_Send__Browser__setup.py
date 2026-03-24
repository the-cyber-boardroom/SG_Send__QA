# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Infrastructure verification — API server, UI server, browser
# ═══════════════════════════════════════════════════════════════════════════════

import requests
from unittest                                                                   import TestCase
from sg_send_qa.browser.SG_Send__Browser__Test_Harness                          import SG_Send__Browser__Test_Harness


class test_SG_Send__Browser__setup(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().setup()
        cls.sg_send = cls.harness.sg_send

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()

    # ── HTTP server checks ───────────────────────────────────────────────────

    def test_api_server__docs(self):
        response = requests.get(self.harness.api_url() + 'api/docs')
        assert response.status_code == 200

    def test_api_server__openapi(self):
        response = requests.get(self.harness.api_url() + 'api/openapi.json')
        assert response.status_code == 200
        assert '/api/transfers/create' in response.json().get('paths', {})

    def test_ui_server__root(self):
        response = requests.get(self.harness.ui_url())
        assert response.status_code == 200

    def test_ui_server__en_gb(self):
        response = requests.get(self.harness.ui_url() + 'en-gb')
        assert response.status_code == 200

    def test_ui_server__qa_setup(self):
        response = requests.get(self.harness.ui_url() + '_common/qa-setup.html')
        assert response.status_code == 200

    # ── Browser checks ───────────────────────────────────────────────────────

    def test_browser__can_open_api_docs(self):
        with self.sg_send.page() as _:
            _.open(self.harness.api_url() + 'api/docs')
            assert _.title() == 'SGraph Send - Swagger UI'

    def test_browser__can_open_ui(self):
        with self.sg_send as _:
            _.page().open(self.harness.ui_url())
            _.wait_for_page_ready()
            assert _.title() == 'SG/Send — Zero-knowledge encrypted file sharing'