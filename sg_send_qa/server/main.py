from fastapi            import FastAPI
from fastapi.responses  import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib            import Path
from sg_send_qa.utils.Version import version__sg_send__qa

app = FastAPI(title="SG/Send QA Test Runner", version=version__sg_send__qa)

repo_root = Path(__file__).parent.parent.parent
site_dir  = repo_root / "sg_send_qa__site"
docs_dir  = site_dir / "pages"


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
    use_cases_dir = docs_dir / "use-cases"
    if use_cases_dir.exists():
        for uc_dir in sorted(use_cases_dir.iterdir()):
            if uc_dir.is_dir():
                for md_file in uc_dir.glob("*.md"):
                    pages.append({"name": uc_dir.name, "path": str(md_file.relative_to(docs_dir))})
    return {"pages": pages}


if site_dir.exists():
    app.mount("/site", StaticFiles(directory=str(site_dir), html=True), name="site")
if docs_dir.exists():
    app.mount("/docs", StaticFiles(directory=str(docs_dir)), name="docs")
