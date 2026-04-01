"""Type_Safe data classes for SG/Send QA.

All data structures used by the QA framework — screenshots, metadata,
group manifests, site summary — defined here as Type_Safe classes.

Import convention:
    from sg_send_qa.models.QA_Types import QA_Use_Case_Metadata, QA_Screenshot

Note: uses Kwargs_To_Self (osbot-utils 3.x) aliased as Type_Safe.
When osbot_utils.base_classes.Type_Safe ships on PyPI, update the import
in sg_send_qa/models/__init__.py and remove the alias.
"""

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self as Type_Safe

# [LIB-2026-04-01-019] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
class QA_Screenshot(Type_Safe):
    """One captured screenshot: name, filesystem path, human description."""
    name        : str
    path        : str = ""
    description : str = ""


class QA_Test_Method(Type_Safe):
    """One test method's contribution to a use-case metadata file."""
    method      : str
    doc         : str  = ""
    screenshots : list          # list of screenshot name strings


class QA_Use_Case_Metadata(Type_Safe):
    """Contents of a use-case _metadata.json file.

    Written by the screenshots fixture after each test run.
    Read by generate_docs to build the site page.
    """
    use_case    : str
    module      : str
    module_doc  : str  = ""
    test_target : str  = "qa_server"   # "qa_server" | "production" | "dev"
    tests       : list                  # list of QA_Test_Method dicts
    screenshots : list                  # list of QA_Screenshot dicts


class QA_Group_Manifest(Type_Safe):
    """Contents of a _group.json file — one per use-case group directory."""
    name        : str
    icon        : str  = ""
    description : str  = ""
    duplicates  : dict          # duplicate_folder → canonical_folder mapping


class QA_Environment_Result(Type_Safe):
    """Test result for one environment (qa_server / production / dev)."""
    status   : str = "not_run"  # "pass" | "fail" | "skip" | "not_run"
    last_run : str = ""          # ISO 8601 timestamp
    error    : str = ""          # failure reason when status == "fail"


class QA_Use_Case_Summary(Type_Safe):
    """Summary row for one use case — used in the dashboard."""
    name             : str
    group            : str  = ""
    screenshot_count : int  = 0
    evidence         : str  = "none"   # "strong" | "good" | "stale" | "none"
    priority         : str  = ""
    composite        : bool = False
    uc_id            : str  = ""


class QA_Group_Summary(Type_Safe):
    """Summary row for one group — used in the dashboard."""
    id            : str
    name          : str
    icon          : str = ""
    total         : int = 0
    with_evidence : int = 0
    coverage_pct  : int = 0


class QA_Site_Summary(Type_Safe):
    """Top-level site summary written to _data/qa_summary.json."""
    generated_at      : str  = ""
    version           : str  = ""
    total_tests       : int  = 0
    total_screenshots : int  = 0
    zero_evidence     : int  = 0
    known_bugs        : int  = 0
    groups            : list          # list of QA_Group_Summary dicts
    needs_attention   : list          # list of use-case names
    missing_tests     : list          # list of use-case names with no test
