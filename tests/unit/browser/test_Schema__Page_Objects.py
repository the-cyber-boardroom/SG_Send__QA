# ═══════════════════════════════════════════════════════════════════════════════
# Unit tests for Schema__*Page page objects
#
# Verifies: Type_Safe inheritance, correct field defaults, field types.
# No browser required — pure data-model tests.
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                           import TestCase
from sg_send_qa.browser.Schema__Upload_Page             import Schema__Upload_Page
from sg_send_qa.browser.Schema__Download_Page           import Schema__Download_Page
from sg_send_qa.browser.Schema__Browse_Page             import Schema__Browse_Page
from sg_send_qa.browser.Schema__Gallery_Page            import Schema__Gallery_Page
from sg_send_qa.browser.Schema__Viewer_Page             import Schema__Viewer_Page


class test_Schema__Upload_Page(TestCase):

    def setUp(self):
        self.schema = Schema__Upload_Page()

    def test__defaults(self):
        assert self.schema.state            == ''
        assert self.schema.file_name        == ''
        assert self.schema.share_link       == ''
        assert self.schema.friendly_token   == ''
        assert self.schema.is_gate_visible  is False

    def test__field_assignment(self):
        self.schema.state           = 'complete'
        self.schema.file_name       = 'test.txt'
        self.schema.share_link      = 'http://localhost/en-gb/browse/#id/key'
        self.schema.friendly_token  = 'apple-mango-1234'
        self.schema.is_gate_visible = True
        assert self.schema.state           == 'complete'
        assert self.schema.file_name       == 'test.txt'
        assert self.schema.share_link      == 'http://localhost/en-gb/browse/#id/key'
        assert self.schema.friendly_token  == 'apple-mango-1234'
        assert self.schema.is_gate_visible is True

    def test__json_roundtrip(self):
        self.schema.state = 'file-ready'
        data = self.schema.json()
        assert data['state'] == 'file-ready'


class test_Schema__Download_Page(TestCase):

    def setUp(self):
        self.schema = Schema__Download_Page()

    def test__defaults(self):
        assert self.schema.state                == ''
        assert self.schema.is_key_input_visible is False
        assert self.schema.content_text         == ''
        assert self.schema.error_message        == ''
        assert self.schema.transfer_id          == ''

    def test__field_assignment(self):
        self.schema.state                = 'complete'
        self.schema.is_key_input_visible = True
        self.schema.content_text         = 'Hello world'
        self.schema.transfer_id          = 'abc123'
        assert self.schema.state                == 'complete'
        assert self.schema.is_key_input_visible is True
        assert self.schema.content_text         == 'Hello world'
        assert self.schema.transfer_id          == 'abc123'


class test_Schema__Browse_Page(TestCase):

    def setUp(self):
        self.schema = Schema__Browse_Page()

    def test__defaults(self):
        assert self.schema.state          == ''
        assert self.schema.content_text   == ''
        assert self.schema.error_message  == ''
        assert self.schema.transfer_id    == ''
        assert self.schema.friendly_token == ''

    def test__field_assignment(self):
        self.schema.state          = 'complete'
        self.schema.friendly_token = 'rose-pine-5678'
        assert self.schema.state          == 'complete'
        assert self.schema.friendly_token == 'rose-pine-5678'


class test_Schema__Gallery_Page(TestCase):

    def setUp(self):
        self.schema = Schema__Gallery_Page()

    def test__defaults(self):
        assert self.schema.state         == ''
        assert self.schema.file_count    == 0
        assert self.schema.content_text  == ''
        assert self.schema.error_message == ''
        assert self.schema.transfer_id   == ''

    def test__field_assignment(self):
        self.schema.file_count = 3
        self.schema.state      = 'complete'
        assert self.schema.file_count == 3
        assert self.schema.state      == 'complete'


class test_Schema__Viewer_Page(TestCase):

    def setUp(self):
        self.schema = Schema__Viewer_Page()

    def test__defaults(self):
        assert self.schema.state         == ''
        assert self.schema.file_name     == ''
        assert self.schema.content_text  == ''
        assert self.schema.error_message == ''
        assert self.schema.transfer_id   == ''

    def test__field_assignment(self):
        self.schema.file_name    = 'document.pdf'
        self.schema.state        = 'complete'
        self.schema.content_text = 'PDF content here'
        assert self.schema.file_name    == 'document.pdf'
        assert self.schema.state        == 'complete'
        assert self.schema.content_text == 'PDF content here'


class test_SG_Send__Browser__Pages__extract_methods(TestCase):
    """Structural tests — verify extract__*() return type annotations are correct.
    Reads source as text to avoid importing osbot_playwright."""

    @classmethod
    def _source(cls):
        from pathlib import Path
        return (Path(__file__).parent.parent.parent.parent /
                'sg_send_qa' / 'browser' / 'SG_Send__Browser__Pages.py').read_text()

    def test__extract_methods_return_annotations(self):
        import ast
        tree    = ast.parse(self._source())
        returns = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('extract__'):
                if node.returns:
                    returns[node.name] = ast.unparse(node.returns)
        assert returns.get('extract__upload_page')   == 'Schema__Upload_Page'
        assert returns.get('extract__download_page') == 'Schema__Download_Page'
        assert returns.get('extract__browse_page')   == 'Schema__Browse_Page'
        assert returns.get('extract__gallery_page')  == 'Schema__Gallery_Page'
        assert returns.get('extract__viewer_page')   == 'Schema__Viewer_Page'

    def test__transfer_id_helper_in_source(self):
        assert '_transfer_id_from_url' in self._source()
