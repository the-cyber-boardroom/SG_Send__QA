# ═══════════════════════════════════════════════════════════════════════════════
# QA_API__Server — backward-compatibility shim
#
# The canonical server is now Fast_API__QA__Server (Serverless__Fast_API).
# This file re-exports `app` so any existing imports still work.
# ═══════════════════════════════════════════════════════════════════════════════
from sg_send_qa.api.Fast_API__QA__Server import app  # noqa: F401  re-export
