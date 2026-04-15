# QA Brief: Browser Persistence Session
**Date:** 2026-04-08
**Source commits:** 0f12d11..61e6602 (origin/dc_offline_development)
**Extracted by:** QA Lead

---

## Summary

This session replaced every ephemeral component in the test harness setup with persistent subprocess-managed alternatives, reducing `SG_Send__Browser__Test_Harness.setup()` from ~3.0 seconds (first-run costs paid every time) to ~31ms on second and subsequent runs. Three new infrastructure classes were introduced — `Server__Base__Local`, `QA__Local_Servers`, and `QA__Local_Browser` — along with a singleton pattern in `QA_Browser`. The primary risk areas are: the reliability of PID-based process reuse across Python process restarts, the correctness of `server__stop()` process group termination, and the freshness of the disk-persisted config files in `.local-servers/`.

---

## @QA Tagged Items

The `@qa` tags in this session were written as inline teaching comments and diagnostic notes rather than formal test requirements. All were found in `tests/qa/apis_for_sites/send_sgraph_ai/pages/test_Page__Send_SGraph_Ai__Upload.py`. The substantive ones:

**1. Commit 7f29d1c — `test_Debug_weird_process_Recycle.test_star_process`:**
```python
# @qa ok the code above is reliably returning:
#   [before] is port open False
#   port 54321
#   [after] is port open True
```
Confirms that `_start_api_server` using `Fast_API_Server` binds and opens the expected port. Implies test case: verify that after `server__start()` the port is confirmed open, and after `server__stop()` it is confirmed closed.

**2. Commit 7f29d1c — same test:**
```python
# @qa ok so the solution is to wire on the SG_Send__Browser__Test_Hardness the use of the external process
```
Records the architectural decision. No direct test obligation, but the implementation that followed (subprocess-based `Server__API__Send_SGraph_AI`) requires full start/stop cycle tests — which were built in `test_Server__API__Send_SGraph_AI.test_server__start____stop`.

**3. Commit 7f29d1c — `test_SG_Send__Browser__Test_Harness__port_reuse`:**
```python
# @qa this looks like the only place where we are testing the _start_api_server,
#       which needs a lot more testing (specially as we add the separate process)
```
Explicit test gap identified. The only test for the API server start path at that point was `test__start_api_server__twice__no_port_conflict`. After refactoring to `Server__API__Send_SGraph_AI`, a full suite was added in `tests/qa/local_servers/test_Server__API__Send_SGraph_AI.py`.

**4. Commit 7f29d1c — `SG_Send__Browser__Test_Harness._load_saved_state`:**
```python
# @qa , the problem of not adding return types to methods like this, is that it not obvious what is the class
@type_safe
def _load_saved_state(self) -> Schema__Harness_State:
```
Not a test case — a code convention note. The `@type_safe` decorator was added as a direct fix. Implies test: `_load_saved_state()` should return a `Schema__Harness_State` instance in debug mode and `None` in headless mode.

**5. Commit 9a2c4eb — `test_setup_and_teardown_headless__false`:**
```python
# @qa so there is not much we can do here since this is inside the Playwright code base
```
Confirms the ~0.2s Playwright context manager start is a fixed cost. Not a test obligation.

**6. Commit 9a2c4eb — same test:**
```python
# @qa ok, so from the data above we can see that the main overhead that we have is
#       a) the playwright sync object creation
#       b) the browser_via_cdp action
#   after that we are having ~90ms to load a 404 and ~150ms to load the full UI
```
Performance baseline established. Implies regression test: time-bound assertions on page load duration.

**7. Commit 751ddb6 — `test_setup_and_teardown_headless__false__using_singleton__qa_browser`:**
```python
# @qa i.e. ~36ms to setup, ~54ms to the 404 page and ~84ms to the main root page
```
Confirmed performance targets for the singleton path. These numbers should become test assertions.

**8. Commit 1ff0cae — `test_Page__Send_SGraph_Ai__Upload__Unit`:**
```python
# @qa we should not be using docstrings for class comments, they should go at the end of the function line
# @qa I think test__init__ is a better name
# @qa for classes that implement type safe, instead of doing this...
# @qa the other problem I can see here is why are we creating a new instance ... for every test method
```
These are code convention notes, not test cases. Pattern established: `test__init__` with `_.obj()` deep assertion is the standard.

---

## New Components — Test Requirements

### Server__Base__Local
**File:** `sg_send_qa/local_servers/Server__Base__Local.py`

Base class for all subprocess-managed local servers. Handles PID tracking, port health checks, config persistence, start/stop lifecycle.

Key methods requiring test coverage:

| Method | Risk |
|--------|------|
| `server__start()` | Calls `config__update()` first — must not double-start if already online |
| `server__stop()` | Uses `os.killpg(os.getpgid(pid), SIGTERM)` — kills process group; verify child processes also die |
| `server__is_running()` | Uses `os.kill(pid, 0)` — will return `True` if PID is reused by a different process after the original died |
| `wait_for__port__open()` | No timeout parameter — will block indefinitely if server fails to start |
| `wait_for__port__closed()` | Same — no timeout |
| `config__update()` | Calls `config__load()` + health checks + `config__save()` in sequence — must be idempotent |
| `server__configured_ok()` | Returns `False` by default — subclasses must override; current behaviour is `server__start()` always returns `False` unless overridden |

**Critical gap:** `server__configured_ok()` is hardcoded to `return False` in the base class. Any subclass that doesn't override it will silently never start. This needs a test.

### Server__API__Send_SGraph_AI
**File:** `sg_send_qa/local_servers/Server__API__Send_SGraph_AI.py` (post-refactor: thin subclass of `Server__Base__Local__Fast_API`)

Manages the SG/Send FastAPI user lambda as a persistent subprocess (port 50001 by default). Launched via `poetry run uvicorn`.

Key methods requiring test coverage:

| Method | Risk |
|--------|------|
| `server__start()` | First call starts uvicorn subprocess; second call must detect running server and return without starting a new one |
| `server__stop()` | Must cleanly terminate the uvicorn process and all children |
| `config__update()` | Checks port AND API health check endpoint; config saved to `.local-servers/server-configs/api__send-sgraph-ai.json` |
| `config__load()` | If JSON file is stale (PID from a previous machine boot, port now used by unrelated process), must handle gracefully |

**Test already in place:** `test_Server__API__Send_SGraph_AI.test_server__start____stop` uses `Temp_Folder` and `random_port` to isolate. This is the right pattern. However, it tests the full start/stop in one method — there is no test for re-entry (calling `server__start()` when the server is already running).

### QA__Local_Servers
**File:** `sg_send_qa/local_servers/QA__Local_Servers.py`

Config persistence manager. Stores server state as JSON files in `.local-servers/server-configs/{server_id}.json`. The `base_folder` field defaults to `sg_send_qa.path` (the package root) — this allows tests to redirect to a temp folder.

Key methods requiring test coverage:

| Method | Risk |
|--------|------|
| `server_config__load()` | If file exists but JSON is malformed, `json_load_file` will raise; no guard |
| `server_config__save()` | Returns `True` only if `server_config__exists()` is True after save — but does not verify content integrity |
| `path__folder__local_servers()` | Resolves to `{sg_send_qa.path}/../.local-servers` — parent traversal; needs to be verified against the actual filesystem |
| `setup()` | Creates folders idempotently — must not fail if called twice |

**Tests in place:** `test_QA__Local_Servers` covers `test__init__`, `test_path__folder__base` (corrected to `test_path__folder__local_servers` in 1dcc0b7), `test_server_config__load`, and `test_setup`. Coverage is reasonable for the happy path. Missing: malformed JSON, concurrent access, missing permissions.

### QA__Local_Browser
**File:** `sg_send_qa/local_servers/QA__Local_Browser.py`

Caches the Chromium executable path to `.local-servers/browser-config.json`. On first call, invokes `chromium_executable_path()` (which starts and stops a full `sync_playwright` instance — ~0.374s). On subsequent calls, reads from disk.

Key methods requiring test coverage:

| Method | Risk |
|--------|------|
| `chromium_executable_path()` | Returns cached value from disk — if Chromium is reinstalled or updated, the stale path will cause failures; no cache invalidation logic |
| `browser_config__update()` | Called automatically when cache file is missing — not when it is stale |
| `browser_config()` | Returns `Schema__Local_Browser__Config` — `chromium_executable_path` is typed as `Safe_Str__File_Path` but is not validated to exist on disk |

**Tests in place:** `test_QA__Local_Browser` covers `test_browser_config` and `test_path__file__browser_config`. Missing: what happens when the cached path no longer exists, and forced cache refresh.

### QA_Browser Singletons
**File:** `sg_send_qa/browser/QA_Browser.py`

Module-level singletons `_qa_browser` and `_qa_browser__headless`, initialised by `qa_browser()` and `qa_browser__headless()` factory functions. `SG_Send__Browser__Pages.qa_browser()` now returns these singletons instead of creating a new `QA_Browser` per call.

Key behaviours requiring test coverage:

| Behaviour | Risk |
|-----------|------|
| Singleton persists across multiple `Page__Send_SGraph_Ai__Upload` instantiations | Verified by `test_setup_and_teardown_headless__false__using_singleton__qa_browser` — but only manually, timing-only assertion |
| Mixed headless/non-headless creates separate singletons | Not tested. The comment in code warns: "at the moment we can't mix headless and non-headless modes, or we get back our async error" |
| Singleton is not reset between test classes | In CI (headless), a stale singleton could hold a dead browser connection between test classes |
| `SG_Send__Browser__Pages.qa_browser()` returns singleton | Not explicitly asserted — `is` identity check missing |

---

## Risk Areas

**1. Stale PID in config file.**
`server__is_running()` checks `os.kill(pid, 0)`. If the OS recycles a PID (common after machine restart), this returns `True` for a process that has nothing to do with the QA servers. `server__start()` will see `server__online = True` and silently skip starting the actual server. The next test will fail attempting to connect to a non-existent service on port 50001.

**2. `server__configured_ok()` defaults to `False`.**
`Server__Base__Local.server__start()` returns `False` immediately if `server__configured_ok()` is `False`. The base implementation returns `False`. If a subclass forgets to override this method, `server__start()` always returns `False` silently. `Server__API__Send_SGraph_AI` and `Server__Http__Send_SGraph_AI` must override it — check that they do.

**3. Lost static config constants (commit 28e89cb warning).**
The commit message explicitly says: "we lost some static config vars what need to be added back and put on a config class." Specifically, `SEND_SGRAPH_AI__SERVER__HOST`, `SEND_SGRAPH_AI__SERVER__SCHEME`, `SEND_SGRAPH_AI__FILE_ID__SERVER_CONFIG`, and `SEND_SGRAPH_AI__SERVER__API__PATH__HEALTH_CHECK` were commented out in `Schema__Server__API__Send_SGraph_AI__Config.py`. If they are now hard-coded inline elsewhere, changes to those values will need to be tracked down manually.

**4. `port_is_open` argument order bug (commit 3cedab1 — fixed, but pattern persists).**
The original `api_server_port_open()` called `port_is_open('localhost', port)` — the positional order was wrong (`port` is the first arg, not `host`). This class of bug (positional arg confusion with common utility functions) is a recurring risk. The fix was to use keyword arguments, which is the correct pattern. Any new call site to `port_is_open`, `is_port_open`, or similar utilities should be reviewed for this.

**5. No timeout on `wait_for__port__open` / `wait_for__port__closed`.**
These methods in `Server__Base__Local` delegate to `wait_for_port` and `wait_for_port_closed` from osbot_utils with no timeout argument. If the server fails to start or stop, the test runner hangs indefinitely. This is a CI risk.

**6. Singleton cannot be reset between test runs.**
The module-level `_qa_browser` and `_qa_browser__headless` globals are set once and never cleared. In a long test session where Chromium is stopped and restarted (e.g. by `QA_Browser.stop()`), the singleton will hold a stale reference. There is currently no `reset_singleton()` utility.

**7. `Schema__Server__Local__Fast_API__Config` imports from `tests/`.**
In `Schema__Server__Local__Fast_API__Config.py` and `Schema__Server__API__Send_SGraph_AI__Config.py`, there is an import: `from tests.qa.local_servers.schemas.safe_str.Safe_Str__Python__FastAPI_Handler import Safe_Str__Python__FastAPI_Handler`. Production code (`sg_send_qa/`) importing from `tests/` is an architectural violation — this will break when the package is installed outside the repo.

---

## Recommended Test Cases

**TEST-001** — `Server__API__Send_SGraph_AI`: start when already running returns False
- Setup: start the server, verify it is online
- Action: call `server__start()` a second time
- Expected: returns `False` (server already running path); no second process spawned
- Priority: P0

**TEST-002** — `Server__API__Send_SGraph_AI`: port is open after `server__start()`, closed after `server__stop()`
- Setup: `Temp_Folder` + `random_port`, start server
- Action: assert port open; call `server__stop()`; assert port closed
- Expected: port state transitions match
- Priority: P0 (already partially covered by `test_server__start____stop`)

**TEST-003** — `Server__Base__Local`: `server__configured_ok()` default is False, subclasses must override
- Action: instantiate `Server__Base__Local()` directly; call `server__start()`
- Expected: returns `False` without spawning any subprocess
- Priority: P0

**TEST-004** — `Server__Base__Local`: `server__stop()` kills process group, not just the top-level PID
- Setup: start a subprocess that spawns a child process; capture both PIDs
- Action: call `server__stop()`
- Expected: both parent and child PIDs are gone after stop
- Priority: P1

**TEST-005** — `Server__API__Send_SGraph_AI` / `QA__Local_Servers`: stale PID in config does not prevent fresh start
- Setup: write a config file with a PID that does not exist (`pid = 99999999`)
- Action: call `server__start()`
- Expected: server detects PID is dead, starts fresh, returns `True`
- Priority: P0

**TEST-006** — `QA__Local_Servers`: `server_config__load()` with malformed JSON returns safe fallback
- Setup: write a corrupt JSON file to the config path
- Action: call `server_config__load(server_id, config_class)`
- Expected: raises a clear exception (or returns default config, whichever is the intended contract); does not return `None` silently
- Priority: P1

**TEST-007** — `QA__Local_Browser`: stale cached path is detected and refreshed
- Setup: write a config file with `chromium_executable_path = '/nonexistent/chrome'`
- Action: call `chromium_executable_path()` on `QA__Local_Browser`
- Expected: either re-queries the actual path and updates cache, or raises a clear `FileNotFoundError`
- Priority: P1

**TEST-008** — `QA_Browser` singletons: `qa_browser()` returns the same object on repeated calls
- Action: call `qa_browser()` twice; compare with `is`
- Expected: `qa_browser() is qa_browser()` is `True`
- Priority: P0

**TEST-009** — `QA_Browser` singletons: headless and non-headless singletons are separate objects
- Action: call `qa_browser()` and `qa_browser__headless()`; compare with `is`
- Expected: they are different objects
- Priority: P0

**TEST-010** — `SG_Send__Browser__Test_Harness`: `_load_saved_state()` returns `None` in headless mode
- Action: instantiate harness with `headless=True`; call `_load_saved_state()`
- Expected: returns `None`
- Priority: P1

**TEST-011** — `SG_Send__Browser__Test_Harness`: `_load_saved_state()` returns `Schema__Harness_State` in debug mode
- Setup: persist a valid `Schema__Harness_State` to disk first
- Action: instantiate harness with `headless=False`; call `_load_saved_state()`
- Expected: returns a `Schema__Harness_State` instance with matching field values
- Priority: P1

**TEST-012** — `Server__Base__Local`: `wait_for__port__open` respects a timeout and does not hang
- Setup: target a port that will never open
- Action: call `wait_for__port__open()` with a short timeout (if the API supports it)
- Expected: returns `False` within the timeout rather than blocking indefinitely
- Priority: P1 — note: currently no timeout parameter is exposed; this test will fail until the API is updated

**TEST-013** — Setup cost regression: second `setup()` call completes in under 100ms
- Setup: run `SG_Send__Browser__Test_Harness.setup()` once (pays full cost); measure second call
- Expected: second call duration < 100ms (current measured baseline ~31ms)
- Priority: P1

**TEST-014** — `Schema__Server__Local__Fast_API__Config` import from `tests/` is absent in package install
- Action: import `sg_send_qa.local_servers.Server__Base__Local__Fast_API` from a clean Python environment without `tests/` on `sys.path`
- Expected: imports successfully
- Priority: P0 — this will break CI when the package is built

**TEST-015** — `QA__Local_Servers.setup()` is idempotent
- Action: call `setup()` twice on the same instance
- Expected: second call returns `self` without error; folders still exist
- Priority: P2 (partially covered; add explicit second-call assertion)

---

## Coverage Gaps

**1. `Server__Base__Local` has no unit tests of its own.**
The file is 171 lines. Current tests only exercise it through `Server__API__Send_SGraph_AI`. The base class methods `server__popen_args()` (raises `NotImplementedError`), `server__configured_ok()` (always `False`), and `health_check__service()` (always `True`) have no direct test coverage. `tests/qa/local_servers/test_Server__Base__Local.py` exists but should be audited for completeness.

**2. `Server__Http__Send_SGraph_AI` — newly introduced, minimal tests.**
This class manages the static file server. `tests/qa/local_servers/test_Server__Http__Send_SGraph_AI.py` was added in commit 28e89cb. It should cover the full start/stop cycle with content-hash-based skip logic.

**3. `Server__Base__Local__Fast_API` — FastAPI health check override.**
`health_check__service()` in this subclass makes an HTTP GET to `/info/status` and validates a JSON response. There are no tests that exercise the case where the health check endpoint returns a non-200 status or a malformed JSON body.

**4. No test for the singleton reset path.**
There is no test (or even a utility) for resetting `_qa_browser` and `_qa_browser__headless` to `None`. This means any test that calls `QA_Browser.stop()` directly will leave the singleton pointing to a dead browser, and subsequent tests in the same Python process will fail silently.

**5. `SG_Send__Browser__Test_Harness.start_ui_server()` — no isolated test.**
The old `_start_ui_server` was never tested directly. The new `start_ui_server()` (which delegates to `Server__Http__Send_SGraph_AI.server__start()`) also has no dedicated unit or integration test. Its interaction with `saved_state.ui_port` branching logic is untested.

**6. `Schema__Server__API__Send_SGraph_AI__Config` import from `tests/` path.**
As noted in Risk Area 7, `Safe_Str__Python__FastAPI_Handler` is imported from `tests/`. This type has no test of its own and its safe-string validation rules are unknown.
