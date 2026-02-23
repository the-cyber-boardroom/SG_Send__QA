# SG/Send QA Automation

Browser automation test suite and living documentation generator for [SG/Send](https://send.sgraph.ai).

## What This Does

- **Automated browser tests** against SG/Send's user and admin interfaces
- **Screenshot capture** at each step of every test
- **Markdown documentation** generated from those screenshots
- **GitHub Pages** publishing for always-up-to-date documentation

Every test run produces two outputs: a **pass/fail result** AND a **documentation page with screenshots**.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
npx playwright install chromium

# Run unit tests
python -m pytest tests/unit/ -v

# Run browser tests against production
TEST_TARGET_URL=https://send.sgraph.ai python -m pytest tests/integration/ -v

# Generate documentation from screenshots
python cli/generate_docs.py

# Start the test runner API
uvicorn server.main:app --port 10070 --reload
```

## CLI Usage

```bash
# Run all tests
python cli/run_tests.py --target https://send.sgraph.ai

# Run a specific test
python cli/run_tests.py --test landing_page

# Run tests and generate docs
python cli/run_tests.py --generate-docs

# Regenerate docs only
python cli/run_tests.py --docs-only
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/info/health` | Health check |
| POST | `/api/tests/run` | Run all tests |
| POST | `/api/tests/run/{test_name}` | Run specific test |
| GET | `/api/tests/results` | Get test results |
| GET | `/api/docs` | Documentation index |

## Project Structure

```
sg_send_qa/         Python package (Version, utilities)
tests/unit/         Unit tests for QA project code
tests/integration/  Browser automation tests
  user/             User Lambda tests
  admin/            Admin Lambda tests
screenshots/        Captured during test runs
docs/               Generated markdown documentation
server/             FastAPI test runner API
cli/                Command-line interface
config/             Test configuration
```

## Test Targets

| Target | URL |
|--------|-----|
| User Lambda (production) | https://send.sgraph.ai |
| Admin Panel (production) | https://send.sgraph.ai/admin/ |
| User Lambda (local) | http://localhost:10062 |
| Admin Lambda (local) | http://localhost:10061 |
