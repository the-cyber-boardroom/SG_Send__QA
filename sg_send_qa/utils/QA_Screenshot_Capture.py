"""Screenshot capture fixture helper for SG/Send QA.

Provides the single canonical ScreenshotCapture implementation.
Previously defined 3 times with divergent metadata schemas
(root conftest, v030 conftest, standalone conftest).

This version uses:
- Module-level grouping (one folder per test module / use case)
- Deduplication on write (no duplicate test entries on re-run)
- QA_Use_Case_Metadata for typed metadata
- cdp_screenshot for the actual capture

Usage (in conftest.py):
    from sg_send_qa.utils.QA_Screenshot_Capture import ScreenshotCapture

    @pytest.fixture
    def screenshots(request):
        capture = ScreenshotCapture.from_request(request)
        yield capture
        capture.save_metadata()
"""

import json
from pathlib import Path

from sg_send_qa.utils.QA_Screenshot import cdp_screenshot


class ScreenshotCapture:
    """Captures screenshots for one test method and persists metadata.

    Groups by module (use case), not by individual test method.
    Multiple test methods in the same module accumulate into one
    _metadata.json (with deduplication on re-run).
    """

    def __init__(self, use_case: str, module_name: str, module_doc: str,
                 method_name: str, shots_dir: Path, test_target: str = "qa_server",
                 method_doc: str = ""):
        self.use_case    = use_case
        self.module_name = module_name
        self.module_doc  = module_doc
        self.method_name = method_name
        self.method_doc  = method_doc
        self.shots_dir   = shots_dir
        self.test_target = test_target
        self._captured: list = []

        shots_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_request(cls, request, base_dir: str = "sg_send_qa__site/pages/use-cases",
                     test_target: str = "qa_server") -> "ScreenshotCapture":
        """Build a ScreenshotCapture from a pytest request object."""
        module_name = request.node.module.__name__.split(".")[-1]
        use_case    = module_name.replace("test__", "")
        method_name = request.node.name
        module_doc  = request.node.module.__doc__ or ""
        method_doc  = request.node.obj.__doc__    or ""

        shots_dir = Path(base_dir) / use_case / "screenshots"
        return cls(
            use_case    = use_case,
            module_name = module_name,
            module_doc  = module_doc,
            method_name = method_name,
            method_doc  = method_doc,
            shots_dir   = shots_dir,
            test_target = test_target,
        )

    def capture(self, page, name: str, description: str = "") -> None:
        """Capture a screenshot and record it."""
        path = self.shots_dir / f"{name}.png"
        cdp_screenshot(page, str(path))
        self._captured.append({
            "name"       : name,
            "path"       : str(path),
            "description": description,
        })

    @property
    def all(self) -> list:
        """All screenshots captured so far."""
        return self._captured

    def save_metadata(self) -> None:
        """Write (or update) _metadata.json with deduplication.

        On re-run, replaces the existing entry for this test method
        rather than appending a duplicate.
        """
        meta_path = self.shots_dir / "_metadata.json"

        if meta_path.exists():
            existing = json.loads(meta_path.read_text())
        else:
            existing = {
                "use_case"   : self.use_case,
                "module"     : self.module_name,
                "module_doc" : self.module_doc,
                "test_target": self.test_target,
                "tests"      : [],
                "screenshots": [],
            }

        # Dedup: replace entry for this method, don't append
        existing["tests"] = [
            t for t in existing["tests"]
            if t.get("method") != self.method_name
        ]
        existing["tests"].append({
            "method"     : self.method_name,
            "doc"        : self.method_doc,
            "screenshots": [s["name"] for s in self._captured],
        })

        # Dedup: replace screenshots by name
        captured_names = {s["name"] for s in self._captured}
        existing["screenshots"] = [
            s for s in existing["screenshots"]
            if s.get("name") not in captured_names
        ]
        existing["screenshots"].extend(self._captured)

        meta_path.write_text(json.dumps(existing, indent=2))
