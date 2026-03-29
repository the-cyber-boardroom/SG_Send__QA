#!/usr/bin/env python3
"""Generate the v2 Web Components site from existing screenshots and metadata.

Reads from:  sg_send_qa__site/pages/use-cases/  (screenshots + _metadata.json)
Writes to:   sg_send_qa__site_v2/pages/use-cases/  (HTML pages)

The existing generator (generate_docs.py → scaffold_page / generate) is
completely untouched. Both generators can run simultaneously:

    python -m sg_send_qa.cli.generate_docs     # v1 — Jekyll markdown
    python -m sg_send_qa.cli.generate_docs_v2  # v2 — Web Components HTML
"""
from sg_send_qa.cli.QA_Generate_Docs import QA_Generate_Docs


def generate_docs_v2():
    QA_Generate_Docs().generate_v2()


if __name__ == "__main__":
    generate_docs_v2()
