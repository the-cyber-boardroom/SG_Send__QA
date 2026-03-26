# ─────────────────────────────────────────────────────────────────────────────
# Run the QA API server locally:
#
#   python -m sg_send_qa.api                      # default: localhost:8000
#   python -m sg_send_qa.api --port 8080          # custom port
#   python -m sg_send_qa.api --host 0.0.0.0       # expose to network
#   python -m sg_send_qa.api --reload             # auto-reload on code changes
#
# Or via uvicorn directly (same result):
#   uvicorn sg_send_qa.api.Fast_API__QA__Server:app --reload
# ─────────────────────────────────────────────────────────────────────────────
import argparse
import uvicorn

parser = argparse.ArgumentParser(description='SG/Send QA API server')
parser.add_argument('--host'  , default='127.0.0.1', help='Bind host (default: 127.0.0.1)')
parser.add_argument('--port'  , default=8000        , type=int, help='Bind port (default: 8000)')
parser.add_argument('--reload', action='store_true'             , help='Auto-reload on code changes')
args = parser.parse_args()

uvicorn.run(
    'sg_send_qa.api.Fast_API__QA__Server:app',
    host   = args.host  ,
    port   = args.port  ,
    reload = args.reload,
)
