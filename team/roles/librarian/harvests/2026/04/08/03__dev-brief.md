# Developer Brief: Browser Persistence Session
**Date:** 2026-04-08
**Source commits:** 0f12d11..61e6602 (origin/dc_offline_development)
**Session theme:** Subprocess-managed server persistence to eliminate test startup cost

---

## Summary

This session solved the core performance problem blocking practical local test development. Before: every test run paid ~1.5 seconds to start the FastAPI server (in-process threading via `Fast_API_Server`). After: the server is launched as a persistent `subprocess.Popen` process on a fixed port (50001), state is written to `.local-servers/server-configs/api__send-sgraph-ai.json`, and subsequent test runs reuse the running process. First run: ~1.5 s. Every run after that: ~15 ms.

A parallel path fixed browser startup cost. `chromium_executable_path()` was calling `sync_playwright().start()` on every construction (~374 ms). That call was extracted to `QA__Local_Browser`, which caches the path to `.local-servers/browser-config.json`. Browser instance connection (`browser_via_cdp`) costs ~395 ms first time; two module-level singletons (`qa_browser()`, `qa_browser__headless()`) in `QA_Browser.py` absorb that cost once per process. Combined result: ~36 ms to `setup()`, ~54 ms to open a page, ~84 ms to load the root page on repeat runs.

The session also produced a clean class hierarchy for local server management: `Server__Base__Local` → `Server__Base__Local__Fast_API` / `Server__Base__Local__Static` → concrete servers.

---

## New Classes & Files

| File | Class | Purpose | Status |
|------|-------|---------|--------|
| `sg_send_qa/local_servers/QA__Local_Servers.py` | `QA__Local_Servers` | Config-file registry: load/save/delete JSON config per server ID from `.local-servers/server-configs/` | Permanent |
| `sg_send_qa/local_servers/Server__Base__Local.py` | `Server__Base__Local` | Base class: subprocess launch, PID tracking, port health check, config persistence, start/stop lifecycle | Permanent |
| `sg_send_qa/local_servers/Server__Base__Local__Fast_API.py` | `Server__Base__Local__Fast_API` | Extends base: uvicorn popen args, JSON health check via `health_check__api()`, `wait_for__server()` via HTTP | Permanent |
| `sg_send_qa/local_servers/Server__Base__Local__Static.py` | `Server__Base__Local__Static` | Extends base: `python -m http.server` popen args, HTTP 200 health check, `server__needs_restart()` content-hash guard | Permanent |
| `sg_send_qa/local_servers/Server__API__Send_SGraph_AI.py` | `Server__API__Send_SGraph_AI` | Thin subclass wiring `Schema__Server__API__Send_SGraph_AI__Config`, fixed port 50001, `server_id = 'api__send-sgraph-ai'` | Permanent |
| `sg_send_qa/local_servers/Server__Http__Send_SGraph_AI.py` | `Server__Http__Send_SGraph_AI` | Thin subclass wiring `Schema__Server__Http__Send_SGraph_AI__Config`, fixed port 50002, `server_id = 'http__send-sgraph-ai'` | Permanent |
| `sg_send_qa/local_servers/schemas/Schema__Server__Local__Config.py` | `Schema__Server__Local__Config` | Base schema: port, host, scheme, process ID, online/started/stopped flags, port health check timestamps | Permanent |
| `sg_send_qa/local_servers/schemas/Schema__Server__Local__Fast_API__Config.py` | `Schema__Server__Local__Fast_API__Config` | Extends base: `fastapi__handler`, `health_check__api__*` fields | Permanent |
| `sg_send_qa/local_servers/schemas/Schema__Server__Local__Static__Config.py` | `Schema__Server__Local__Static__Config` | Extends base: `health_check__http__*`, `ui__serve_dir`, `ui__content_hash` | Permanent |
| `sg_send_qa/local_servers/schemas/Schema__Server__API__Send_SGraph_AI__Config.py` | `Schema__Server__API__Send_SGraph_AI__Config` | Concrete: `fastapi__handler` = `sgraph_ai_app_send...lambda_handler__user:app`, `server__port = 50001` | Permanent |
| `sg_send_qa/local_servers/schemas/Schema__Server__Http__Send_SGraph_AI__Config.py` | `Schema__Server__Http__Send_SGraph_AI__Config` | Concrete: `server__port = 50002` | Permanent |
| `sg_send_qa/local_servers/QA__Local_Browser.py` | `QA__Local_Browser` / `Schema__Local_Browser__Config` | Caches Chromium executable path to `.local-servers/browser-config.json`; eliminates ~374 ms `sync_playwright().start()` per test construction | Permanent |
| `sg_send_qa/browser/for__osbot_playwright/chromium_executable_path.py` | `chromium_executable_path()` | Extracted function (was inline in `SG_Send__Playwright_Browser__Chrome`); avoids circular import | Permanent — but flagged for refactor into `QA__Local_Browser` |
| `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Browse.py` | `Page__Send_SGraph_Ai__Browse` | Browse page object (file existed, session added `@dev` casing note) | Permanent |
| `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Download.py` | `Page__Send_SGraph_Ai__Download` | Download page object | Permanent |
| `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Gallery.py` | `Page__Send_SGraph_Ai__Gallery` | Gallery page object | Permanent |

---

## Key Technical Decisions

### 1. Subprocess over threading for the API server

**Problem (commit 7f29d1c):** `Fast_API_Server.start()` uses `threading.Thread`. When the test process exits, the thread dies. The server cannot survive test runs. Port-reuse logic in `SG_Send__Browser__Test_Harness._start_api_server()` was wasted because the thread was always dead on next invocation.

**Decision:** Replace with `subprocess.Popen(["poetry", "run", "uvicorn", ...])`. The child process outlives the test process. On the next run, `config__update()` detects the port is already open and skips launch entirely.

**Result:** First run ~1.35 s (uvicorn startup), all subsequent runs ~15 ms (port already open).

### 2. Config persistence via JSON files in `.local-servers/`

`QA__Local_Servers` writes server state (PID, port, health check results, started/stopped flags) to `.local-servers/server-configs/{server_id}.json`. This lets the QA process rediscover a running server after restart without maintaining a daemon or registry service. The folder is gitignored.

### 3. `os.killpg` for subprocess termination

In `Server__Base__Local.server__stop()`, the session switched from `stop_process(pid)` to `os.killpg(os.getpgid(pid), signal.SIGTERM)`. The process group kill ensures child processes (e.g. worker threads spawned by uvicorn) are also terminated, preventing zombie port occupation.

### 4. Singleton browser instances to eliminate connection cost

`browser_via_cdp` costs ~395 ms. `sync_playwright().start()` costs ~374 ms. These are unavoidable on first call but need only happen once per Python process. Two module-level singletons in `QA_Browser.py` (`qa_browser()` / `qa_browser__headless()`) hold live `QA_Browser` instances. `SG_Send__Browser__Pages.qa_browser()` now delegates to these rather than constructing a new instance every time.

**Constraint (noted in code):** Headless and non-headless modes cannot be mixed in the same process — Playwright raises `"It looks like you are using Playwright Sync API inside the asyncio loop"`. The two separate singletons are the workaround.

### 5. Chromium path caching via `QA__Local_Browser`

`chromium_executable_path()` was called once per `SG_Send__Playwright_Browser__Chrome` construction (commit 38d77d3 measured it at ~374 ms). `QA__Local_Browser` caches the resolved path to `.local-servers/browser-config.json`. If the file exists the path is read from disk (near-zero cost); if not, it calls `chromium_executable_path()` once and writes the result.

### 6. Static config vars lost in refactoring

Commit 28e89cb (the Claude-assisted refactoring into the base hierarchy) commented out several module-level constants (`SEND_SGRAPH_AI__SERVER__HOST`, `SEND_SGRAPH_AI__SERVER__SCHEME`, `SEND_SGRAPH_AI__FILE_ID__SERVER_CONFIG`, `SEND_SGRAPH_AI__SERVER__API__PATH__HEALTH_CHECK`) that existed in the original monolithic `Server__API__Send_SGraph_AI`. Their values are now hardcoded in base schema defaults. The comment in `Schema__Server__API__Send_SGraph_AI__Config` explicitly flags this: `@dev can you review the last commit removals since we lost in the factoring some of these static values`.

---

## @Dev Tagged Items

All `@Dev` comments found in the session diff, with recommended action IDs:

| # | Comment (verbatim) | File / Location | Recommended Action |
|---|--------------------|-----------------|--------------------|
| 1 | `@dev can you refactor this (and others) to Page__Send_SGraph_AI__Browse (since we should be using "AI" not "Ai")` | `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Browse.py` | REFACTOR-001: rename all `Page__Send_SGraph_Ai__*` classes/files to `Page__Send_SGraph_AI__*` |
| 2 | `@dev theis setup feels quite generic and should be moved to a base class that Page__Send_SGraph_Ai__Upload then uses` | `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Upload.py` — `setup()` | REFACTOR-002: extract common page setup into `Page__Send_SGraph_AI__Base` |
| 3 | `@dev todo: see if there is a better way to do this (so that we don't have two methods here)` | `sg_send_qa/browser/QA_Browser.py` — module-level singletons `qa_browser()` / `qa_browser__headless()` | TASK-001: investigate a single parameterised singleton factory or a headless-keyed dict |
| 4 | `@dev note that at the moment we can't mix headless and non-headless modes, or we get back our async error` | `sg_send_qa/browser/SG_Send__Browser__Pages.py` — `qa_browser()` method | TASK-002: document Playwright asyncio limitation; consider process isolation if mixing is needed |
| 5 | `@dev todo: with the new mode to start the api server, do we still need this? ... FastAPI on stable port (in-memory backend)` | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` — `api_server: Fast_API_Server` field | TASK-003: determine whether `api_server` field is still needed; remove if not |
| 6 | `@dev see what we need to do with this saved_state` | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` — `setup()` call to `start_api_server` | REFACTOR-003: clarify or remove `saved_state` threading through new subprocess-based start path |
| 7 | `@dev refactor these test_objs for one that works with the local server/process we just started` | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` — `access_token()` method | REFACTOR-004: replace `Send__User_Lambda__Test_Objs`-based token retrieval with direct HTTP call to local server |
| 8 | `@dev see what refactorings we can do this (also see what we should do with the saved state)` | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` — `start_ui_server()` | REFACTOR-003 (same): clarify saved_state role in the new subprocess path |
| 9 | `todo: @dev fix this setup workflow (since we shouldn't need to have all these checks here), namely around how the saved_state is wired up` | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` — `start_ui_server()` inner block | REFACTOR-003 (same) |
| 10 | `@dev following on the comment I left on _ui_content_hash, not only that was not an efficient way to do this, we were calling it twice` | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` — `build_ui()` | TASK-004: ensure `ui_content_hash()` is computed once and passed through; not recomputed in build and in start |
| 11 | `@dev can you map out the scenario where we add a couple more hashes and version numbers to each UI core manifest` | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` — `build_ui()` | TASK-005: design manifest schema for UI build identity (hash, version, timestamp) |
| 12 | `@dev use Safe_Id once default value auto-conversion is confirmed` (×2) | `sg_send_qa/local_servers/Server__API__Send_SGraph_AI.py` and `Server__Http__Send_SGraph_AI.py` — `server_id` field | TASK-006: switch `server_id: str` to `server_id: Safe_Id` once Type_Safe default value coercion is verified |
| 13 | `todo: @dev add checks to make sure all vars valued to safely create the process are correctly set up (see how the __Static was implemented)` | `sg_send_qa/local_servers/Server__Base__Local__Fast_API.py` — `server__configured_ok()` | TASK-007: implement `server__configured_ok()` with real validation in `Server__Base__Local__Fast_API` (mirrors `Server__Base__Local__Static`) |
| 14 | `@dev can you review the last commit removals since we lost in the factoring some of these static values and started to use hard-coded primitives variables in the code` | `sg_send_qa/local_servers/schemas/Schema__Server__API__Send_SGraph_AI__Config.py` — module constants | REFACTOR-005: restore named module-level constants for HOST, SCHEME, health check path; replace implicit schema defaults |
| 15 | `@dev: move to common config location` | Same file — `SEND_SGRAPH_AI__SERVER__PORT` | REFACTOR-005 (same): centralise port constants |
| 16 | `@dev: I think an Enum would be better here` | Same file — `server__scheme` | TASK-008: introduce `Safe_Str__Url__Scheme` or Enum for HTTP/HTTPS scheme |
| 17 | `@dev if we call this twice, we get the error "playwright._impl._errors.Error: It looks like you are using Playwright Sync API inside the asyncio loop."` | `tests/qa/apis_for_sites/.../test_Page__Send_SGraph_Ai__Upload.py` | TASK-002 (same as #4): document + guard against double-start |
| 18 | `@dev add support for this pattern to OSBot_Utils` (duration comparison) | Same test file | TASK-009: upstream to OSBot_Utils — `assert duration__teardown < 0.5` syntax support |
| 19 | `@dev fix in OSBot_Utils` (×2, `ui_folder` and `ui_server` not Type_Safe) | Same test file | TASK-010: upstream to OSBot_Utils — `ui_folder` / `ui_server` Type_Safe conformance |

---

## Breaking Changes

### `SG_Send__Browser__Test_Harness._start_api_server()` → replaced

The old `_start_api_server()` used `Fast_API_Server` (in-process threading). It is now replaced by `start_api_server()` (public, no leading underscore) which delegates entirely to `self.server__send_graph_ai__api.server__start()`. The `saved_state` parameter is still accepted but its `api_port` is no longer used — the port is fixed at 50001 via `Schema__Server__API__Send_SGraph_AI__Config`.

**Callers that must update:** Any code that calls `_start_api_server(saved_state)` directly should call `start_api_server()` instead. Any code that reads `harness.api_server.port` must now read `harness.server__send_graph_ai__api.config.server__port`.

### `SG_Send__Browser__Test_Harness._start_ui_server()` → replaced

Replaced by `start_ui_server()` (public), which delegates to `self.server__send_graph_ai__http`. The old `Temp_Web_Server`-based implementation is commented out but not deleted.

### `SG_Send__Browser__Pages.qa_browser()` → singleton-backed

Previously constructed a new `QA_Browser(headless=self.headless)` on every call (guarded by `@cache_on_self`). Now returns the module-level singleton from `qa_browser()` or `qa_browser__headless()`. The first call still pays the full browser connection cost; subsequent calls across different objects in the same process pay nothing.

### `SG_Send__Playwright_Browser__Chrome.browser_exec_path` assignment

Previously called `chromium_executable_path()` inline in `__init__` (the slow version with `sync_playwright().start()`). Now calls `QA__Local_Browser().chromium_executable_path()` which reads from the file cache. Any code that monkey-patched or mocked `chromium_executable_path` in tests must update its import path: the function now lives in `sg_send_qa/browser/for__osbot_playwright/chromium_executable_path.py`.

---

## Temporary Scaffolding to Remove

| Item | Location | Description |
|------|----------|-------------|
| Commented-out `_start_api_server` body | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` lines ~140-155 | Old `Fast_API_Server` threading approach; preserved as context, should be deleted once new path is stable |
| Commented-out `_start_ui_server` body | Same file, `start_ui_server()` | Old `Temp_Web_Server` approach; same disposition |
| `print_duration` instrumentation in `test_setup_and_teardown_headless__false` | `tests/qa/apis_for_sites/.../test_Page__Send_SGraph_Ai__Upload.py` | Measurement scaffolding; comment-block of commented-out probe lines should be cleaned up |
| `test_setup_and_teardown_headless__false` test itself | Same file | Discovery test, not an assertion test; either promote to a real timing assertion (`assert duration < X`) or delete |
| `test_setup_and_teardown_headless__false__using_singleton__qa_browser` | Same file | Exploratory test that proved the singleton works; should be replaced with a proper regression test |
| `print_duration` import in `Server__API__Send_SGraph_AI` initial commit | Cleaned up by 28e89cb refactor — no action needed | Already gone from final file state |

---

## Refactoring Backlog

| ID | File | Issue | Action | Priority |
|----|------|-------|--------|----------|
| REFACTOR-001 | `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Browse.py` (and `__Download`, `__Gallery`, `__Upload`) | Class and file names use `Ai` casing; should be `AI` | Rename all four page classes and files to `Page__Send_SGraph_AI__*`; update all imports | High |
| REFACTOR-002 | `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Upload.py` | `setup()` logic is duplicated across page classes | Extract `Page__Send_SGraph_AI__Base` with common `setup()`, `teardown()`, `headless()` | Medium |
| REFACTOR-003 | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` | `saved_state` is threaded into `start_api_server()` and `start_ui_server()` but both new methods mostly ignore it | Define what saved_state means for the subprocess path; either remove or replace with direct config queries | Medium |
| REFACTOR-004 | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` — `access_token()` | Still uses `Send__User_Lambda__Test_Objs`; tied to in-process test client | Replace with HTTP call to the local subprocess server to obtain token; remove `Send__User_Lambda__Test_Server` dependency from harness | Medium |
| REFACTOR-005 | `sg_send_qa/local_servers/schemas/Schema__Server__API__Send_SGraph_AI__Config.py` | Module constants for HOST, SCHEME, health check path were lost in refactoring; values are implicit defaults in base schema | Restore named constants; add `SEND_SGRAPH_AI__SERVER__HOST`, `SEND_SGRAPH_AI__SERVER__SCHEME`, `SEND_SGRAPH_AI__SERVER__API__PATH__HEALTH_CHECK` as explicit module-level values | Low |
| REFACTOR-006 | `sg_send_qa/local_servers/QA__Local_Servers.py` | `server_config__load/save/delete/exists` methods are a mini config-registry; comment says "todo: refactor into separate class" | Extract `Server__Config__Registry` from `QA__Local_Servers` | Low |

---

## What Still Needs Tests

| Code | Gap | Suggested Test File |
|------|-----|---------------------|
| `Server__Base__Local.server__start()` full round-trip | Only concrete subclass tests exist; base class `server__start()` is never called directly with a `server__popen_args()` implementation | `tests/qa/local_servers/test_Server__Base__Local.py` — add a minimal subclass fixture |
| `Server__Base__Local__Fast_API.server__configured_ok()` | Returns `True` unconditionally; no validation. The `@dev` tag says it needs real checks. No test for the failure path. | `tests/qa/local_servers/test_Server__Base__Local__Fast_API.py` — add test once implementation is done |
| `QA__Local_Browser.browser_config__update()` | Cache invalidation not tested; no test for stale or missing file path | `tests/qa/local_servers/test_QA__Local_Browser.py` |
| `QA_Browser` module-level singletons `qa_browser()` / `qa_browser__headless()` | No test verifies singleton identity across multiple calls; no test verifies the asyncio error is actually raised when mixing modes | `tests/qa/browser/test_QA_Browser.py` |
| `SG_Send__Browser__Test_Harness.start_api_server()` and `start_ui_server()` new subprocess paths | `test__start_api_server__twice__no_port_conflict` exists for the old path; no equivalent for the new subprocess-based methods | `tests/unit/browser/test_SG_Send__Browser__Test_Harness.py` — add tests for new paths |
| `SG_Send__Browser__Test_Harness.access_token()` post-refactor | Currently untested; returns from `test_objs` which is populated by the old in-process path | Add test once REFACTOR-004 is complete |
| `Schema__Server__Local__Config` field-level validation | No test verifies that invalid port numbers, missing hosts, etc., are rejected by the schema | `tests/qa/local_servers/schemas/test_Schema__Server__Local__Config.py` |
