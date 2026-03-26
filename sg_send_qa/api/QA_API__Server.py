# ═══════════════════════════════════════════════════════════════════════════════
# QA_API__Server — FastAPI application for the SG/Send QA API
#
# Entry point: from sg_send_qa.api.QA_API__Server import app
# ═══════════════════════════════════════════════════════════════════════════════
from fastapi                                        import FastAPI
from sg_send_qa.api.routes.routes__browser          import router as browser_router

app = FastAPI(title="SG/Send QA API", version="0.2.30",
              description="Stateless browser automation API for SG/Send QA")

app.include_router(browser_router)


@app.get("/api/qa/health")
def health():
    return {"status": "ok", "version": "0.2.30"}
