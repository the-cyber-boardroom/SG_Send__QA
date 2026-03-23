"""Type_Safe class for the SG/Send QA test runner CLI.

Usage:
    runner = QA_Run_Tests(target="https://send.sgraph.ai")
    runner.run()
"""
import os
import subprocess
import sys

from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self as Type_Safe


class QA_Run_Tests(Type_Safe):
    target       : str  = "https://send.sgraph.ai"
    test         : str  = ""
    generate_docs: bool = False
    docs_only    : bool = False
    tests_path   : str  = "tests/integration/"

    def run(self) -> int:
        """Execute the requested test run.

        Returns the pytest exit code (0 = all pass).
        """
        if self.docs_only:
            print("Regenerating documentation from existing screenshots...")
            self._run_generate_docs()
            return 0

        os.environ["TEST_TARGET_URL"] = self.target

        cmd = [sys.executable, "-m", "pytest", self.tests_path, "-v"]
        if self.test:
            cmd.extend(["-k", self.test])

        print(f"Running tests against: {self.target}")
        result = subprocess.run(cmd)

        if self.generate_docs:
            print("Generating documentation...")
            self._run_generate_docs()

        return result.returncode

    def _run_generate_docs(self) -> None:
        from sg_send_qa.cli.QA_Generate_Docs import QA_Generate_Docs
        QA_Generate_Docs().generate()

    @classmethod
    def from_args(cls, args) -> "QA_Run_Tests":
        """Build a QA_Run_Tests instance from a parsed argparse namespace."""
        return cls(
            target        = args.target,
            test          = args.test or "",
            generate_docs = args.generate_docs,
            docs_only     = args.docs_only,
        )
