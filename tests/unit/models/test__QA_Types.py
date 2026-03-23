"""Unit tests for sg_send_qa.models.QA_Types."""

from sg_send_qa.models.QA_Types import (
    QA_Screenshot,
    QA_Test_Method,
    QA_Use_Case_Metadata,
    QA_Group_Manifest,
    QA_Environment_Result,
    QA_Use_Case_Summary,
    QA_Group_Summary,
    QA_Site_Summary,
)


class TestQA_Screenshot:
    def test_defaults(self):
        s = QA_Screenshot(name="01_landing")
        assert s.name        == "01_landing"
        assert s.path        == ""
        assert s.description == ""

    def test_all_fields(self):
        s = QA_Screenshot(name="01_landing", path="/tmp/01.png", description="Landing page")
        assert s.path        == "/tmp/01.png"
        assert s.description == "Landing page"

    def test_json(self):
        s    = QA_Screenshot(name="shot", path="/p", description="d")
        data = s.json()
        assert data["name"]        == "shot"
        assert data["path"]        == "/p"
        assert data["description"] == "d"


class TestQA_Test_Method:
    def test_defaults(self):
        m = QA_Test_Method(method="test_something")
        assert m.method      == "test_something"
        assert m.doc         == ""
        assert m.screenshots == []

    def test_screenshots_not_shared(self):
        a = QA_Test_Method(method="a")
        b = QA_Test_Method(method="b")
        a.screenshots.append("01_shot")
        assert b.screenshots == []          # must not share mutable default


class TestQA_Use_Case_Metadata:
    def test_defaults(self):
        m = QA_Use_Case_Metadata(use_case="access_gate", module="test__access_gate")
        assert m.test_target == "qa_server"
        assert m.module_doc  == ""
        assert m.tests       == []
        assert m.screenshots == []

    def test_lists_not_shared(self):
        a = QA_Use_Case_Metadata(use_case="a", module="test__a")
        b = QA_Use_Case_Metadata(use_case="b", module="test__b")
        a.tests.append({"method": "x"})
        assert b.tests == []


class TestQA_Group_Manifest:
    def test_defaults(self):
        g = QA_Group_Manifest(name="Access Gate")
        assert g.icon        == ""
        assert g.description == ""
        assert g.duplicates  == {}

    def test_with_icon(self):
        g = QA_Group_Manifest(name="Upload", icon="upload")
        assert g.name == "Upload"
        assert g.icon == "upload"

    def test_duplicates_not_shared(self):
        a = QA_Group_Manifest(name="a")
        b = QA_Group_Manifest(name="b")
        a.duplicates["x"] = "y"
        assert b.duplicates == {}


class TestQA_Environment_Result:
    def test_defaults(self):
        r = QA_Environment_Result()
        assert r.status   == "not_run"
        assert r.last_run == ""
        assert r.error    == ""

    def test_pass(self):
        r = QA_Environment_Result(status="pass", last_run="2026-03-23T10:00:00Z")
        assert r.status == "pass"


class TestQA_Use_Case_Summary:
    def test_defaults(self):
        s = QA_Use_Case_Summary(name="access_gate")
        assert s.group            == ""
        assert s.screenshot_count == 0
        assert s.evidence         == "none"
        assert s.composite        is False

    def test_strong_evidence(self):
        s = QA_Use_Case_Summary(name="combined_link", evidence="strong", screenshot_count=7)
        assert s.evidence         == "strong"
        assert s.screenshot_count == 7


class TestQA_Group_Summary:
    def test_defaults(self):
        g = QA_Group_Summary(id="01-access-gate", name="Access Gate")
        assert g.icon          == ""
        assert g.total         == 0
        assert g.with_evidence == 0
        assert g.coverage_pct  == 0


class TestQA_Site_Summary:
    def test_defaults(self):
        s = QA_Site_Summary()
        assert s.total_tests       == 0
        assert s.total_screenshots == 0
        assert s.zero_evidence     == 0
        assert s.known_bugs        == 0
        assert s.groups            == []
        assert s.needs_attention   == []
        assert s.missing_tests     == []

    def test_lists_not_shared(self):
        a = QA_Site_Summary()
        b = QA_Site_Summary()
        a.groups.append("x")
        assert b.groups == []
