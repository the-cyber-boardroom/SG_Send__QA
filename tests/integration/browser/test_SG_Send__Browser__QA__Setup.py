from unittest                                                               import TestCase
from sg_send_qa.browser.SG_Send__Browser__Test_Harness import SG_Send__Browser__Test_Harness


class test_SG_Send__Browser__setup(TestCase):                            # Page state queries
    @classmethod
    def setUpClass(cls):
        cls.harness = SG_Send__Browser__Test_Harness().setup()
        cls.sg_send = cls.harness.sg_send

    @classmethod
    def tearDownClass(cls):
        cls.harness.teardown()


    # ── QA Setup ───────────────────────────────────────────────────────

    def test__page__qa_setup(self):
        with self.sg_send as _:
            assert _.page__qa_setup().url() == f'http://localhost:{self.harness.ui_server.port}/_common/qa-setup.html'
            assert _.title()                == 'QA Setup'

    def test__storage__dump(self):
        with self.sg_send as _:
            qa_dump = _.storage__dump()
            assert qa_dump == {}

    def test__storage__set_token(self):
        token = 'an-token'
        with self.sg_send as _:
            qa_dump = _.storage__set_token(token).storage__dump()
            assert qa_dump == {'sgraph-send-token': token }
