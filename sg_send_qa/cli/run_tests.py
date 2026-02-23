#!/usr/bin/env python3
"""SG/Send QA Test Runner CLI.

Usage:
    python -m sg_send_qa.cli.run_tests --target https://send.sgraph.ai
    python -m sg_send_qa.cli.run_tests --test user.test_landing_page
    python -m sg_send_qa.cli.run_tests --generate-docs
    python -m sg_send_qa.cli.run_tests --docs-only
"""
import argparse
import os
import subprocess
import sys


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

    if args.docs_only:
        print("Regenerating documentation from existing screenshots...")
        from sg_send_qa.cli.generate_docs import generate_docs
        generate_docs()
        return

    os.environ["TEST_TARGET_URL"] = args.target

    cmd = [sys.executable, "-m", "pytest", "tests/integration/", "-v"]
    if args.test:
        cmd.extend(["-k", args.test])

    print(f"Running tests against: {args.target}")
    result = subprocess.run(cmd)

    if args.generate_docs:
        print("Generating documentation...")
        from sg_send_qa.cli.generate_docs import generate_docs
        generate_docs()

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
