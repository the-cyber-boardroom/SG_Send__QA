#!/usr/bin/env python3
"""Thin wrapper — implementation lives in QA_Generate_Docs.

Kept so `python -m sg_send_qa.cli.generate_docs` still works (CI pipeline).
"""
from sg_send_qa.cli.QA_Generate_Docs import QA_Generate_Docs


def generate_docs():
    QA_Generate_Docs().generate()


if __name__ == "__main__":
    generate_docs()
