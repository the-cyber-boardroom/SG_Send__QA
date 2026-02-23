from fastapi            import FastAPI
from fastapi.responses  import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib            import Path
from sg_send_qa.utils.Version import version__sg_send__qa

app = FastAPI(title="SG/Send QA Test Runner", version=version__sg_send__qa)

docs_dir        = Path(__file__).parent.parent / "docs"
screenshots_dir = Path(__file__).parent.parent / "screenshots"


@app.get("/info/health")
def health():
    return {"status": "ok", "service": "sg_send__qa", "version": version__sg_send__qa}


@app.post("/api/tests/run")
def run_all_tests():
    return {"status": "not_implemented"}


@app.post("/api/tests/run/{test_name}")
def run_test(test_name: str):
    return {"status": "not_implemented", "test": test_name}


@app.get("/api/tests/results")
def get_results():
    return {"results": []}


@app.get("/api/docs")
def get_docs_index():
    pages = []
    if docs_dir.exists():
        for md_file in sorted(docs_dir.glob("*.md")):
            pages.append({"name": md_file.stem, "path": str(md_file.relative_to(docs_dir))})
    return {"pages": pages}


if docs_dir.exists():
    app.mount("/docs", StaticFiles(directory=str(docs_dir)), name="docs")
if screenshots_dir.exists():
    app.mount("/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")
