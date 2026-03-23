#!/usr/bin/env python3
"""Thin wrapper — implementation lives in QA_Diff_Screenshots.

Kept so `python -m sg_send_qa.ci.diff_screenshots` still works (CI pipeline).
"""
from sg_send_qa.ci.QA_Diff_Screenshots import QA_Diff_Screenshots


def main():
    QA_Diff_Screenshots().run()


if __name__ == "__main__":
    main()
