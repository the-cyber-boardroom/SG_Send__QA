#!/usr/bin/env python3
"""Thin wrapper — implementation lives in QA_Run_Tests.

Usage:
    python -m sg_send_qa.cli.run_tests --target https://send.sgraph.ai
    python -m sg_send_qa.cli.run_tests --test user.test_landing_page
    python -m sg_send_qa.cli.run_tests --generate-docs
    python -m sg_send_qa.cli.run_tests --docs-only
"""
import argparse
import sys

from sg_send_qa.cli.QA_Run_Tests import QA_Run_Tests

# [LIB-2026-04-01-022] see: team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md
def main():
    parser = argparse.ArgumentParser(description="SG/Send QA Test Runner")
    parser.add_argument("--target", default="https://send.sgraph.ai",
                        help="Target URL to test (default: https://send.sgraph.ai)")
    parser.add_argument("--test", default=None,
                        help="Specific test to run (e.g., user.test_landing_page)")
    parser.add_argument("--generate-docs", action="store_true",
                        help="Generate markdown docs after tests")
    parser.add_argument("--docs-only", action="store_true",
                        help="Regenerate docs from existing screenshots")
    args = parser.parse_args()

    runner = QA_Run_Tests.from_args(args)
    sys.exit(runner.run())


if __name__ == "__main__":
    main()
