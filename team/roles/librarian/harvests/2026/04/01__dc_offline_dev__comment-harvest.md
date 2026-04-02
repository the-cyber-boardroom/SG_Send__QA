# Comment Harvest — dc_offline_dev session

**Harvest date:** 2026-04-01
**Harvested by:** Librarian (claude/librarian-comment-harvest-8xeEK)
**Status:** Complete — comments removed from source, tracking refs placed

---

## A. Session Overview

| Field | Value |
|-------|-------|
| **Author** | Dinis Cruz |
| **Date** | 2026-03-31 |
| **Branch** | `origin/dc_offline_development` |
| **Commits** | b34a9117 → 17daf799 (6 substantive commits) |
| **Brief** | `team/humans/dinis_cruz/briefs/04/01/v0.19.7__brief__offline-mode-local-llms.md` |

Dinis spent a focused offline session instrumenting the browser test harness with `print_duration` calls to locate the performance bottlenecks in `setup()`. He annotated the source with `# todo:` comments as a deliberate human→agent communication channel (described in brief v0.19.7), capturing architectural observations, raw timing data, refactoring instructions, and explicit directives to the Developer, QA, and Architect roles. The session culminated in a proof-of-concept (`debug__start_and_stop_server_using_port`) demonstrating that a long-lived uvicorn process controlled by PID can eliminate the ~300 ms per-test startup cost.

---

## B. Examples: The Pattern In Action

These are five concrete examples showing how the `# todo:` comment-as-communication pattern works in practice — each a different type of signal.

---

### Example 1 — Architectural Observation (something is wrong with the design)

**File:** `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py`, line 32

**Comment text:**
```python
# todo: split this class into smaller parts/concernts since it is already doing too much
#       rename sg_send to something that is related to what it is actualy doing
```

**What it communicates:** The author identified that `SG_Send__Browser__Test_Harness` has violated the Single Responsibility Principle. It manages API server lifecycle, UI server lifecycle, browser creation, state persistence, and token injection — five distinct concerns in one class. The attribute `sg_send` is also a misleading name since it holds a `SG_Send__Browser__Pages` instance (a page abstraction), not a connection to the SG/Send service.

**Why it is a good example:** This is a structural observation that cannot be captured in a commit message. The author was deep in the code, noticed the problem, and left a message for the refactoring agent rather than stopping the debugging session to fix it. The comment travels with the code until it is processed.

---

### Example 2 — Refactoring Instruction (how something should be changed)

**File:** `sg_send_qa/browser/JS_Query__Execute.py`, line 68

**Comment text:**
```python
# todo: refactor this into a separate class (focused only on LocalStorage
```

**What it communicates:** The `localStorage` methods (`storage_get`, `storage_set`, `storage_remove`, `storage_clear`, `storage_dump`) have been grouped together in `JS_Query__Execute` but belong in their own class. Similarly, the light DOM read methods and the predicate methods also carry `# todo: refactor this into a separate class` — three distinct groupings inside one file that should each become a class. The comment on line 68 is the first in a chain that flags the same structural issue across the file.

**Why it is a good example:** This is not a vague "clean up" note. It tells the Developer exactly what to extract and why (focus). The three identical comments across different method groups make the decomposition strategy explicit: extract `JS_Query__LocalStorage`, `JS_Query__LightDOM`, and `JS_Query__Predicates` (or similar).

---

### Example 3 — Performance Data Point (raw timing captured inline)

**File:** `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Upload.py`, lines 111–128

**Comment text:**
```python
# todo: here are the inner duration captures

# action "_load_saved_state" took: 0.0 seconds
# action "_start_api_server" took: 0.24 seconds
# action "_build_ui" took: 0.107 seconds
# action "_start_ui_server" took: 0.005 seconds
# action "_create_browser" took: 0.0 seconds
# action "_save_state" took: 0.0 seconds
# action "capture_stderr" took: 0.0 seconds
```

**What it communicates:** This is raw profiling output pasted inline while the developer was running `debug_inner_calls_of_setup()`. Two runs of data confirm the pattern: `_start_api_server` (~230 ms) and `_build_ui` (~105 ms) together account for the entire 300 ms budget. Everything else is effectively free. This data is the foundation for the optimization strategy (section E).

**Why it is a good example:** This is the most literal form of the pattern — the developer pastes the program's own output back into the source as a comment. The data lives in the exact function it describes, with zero distance between observation and evidence. The agent processing it does not need to re-run the benchmarks; it has the numbers.

---

### Example 4 — Agent Directive (explicitly addressed to a named role)

**File:** `tests/qa/apis_for_sites/send_sgraph_ai/pages/test_Page__Send_SGraph_Ai__Upload.py`, line 94

**Comment text:**
```python
# @dev @architect capture this pattern of using the OSbot_Utils __() and obj() and Type_Safe().obj() technique to write powerful assertions like the one below
```

**What it communicates:** Two roles are addressed explicitly. The Developer should document how the `__()` / `obj()` / `Type_Safe().obj()` assertion pattern works so it becomes the standard. The Architect should evaluate whether this pattern warrants a dedicated section in the coding standards. The comment is placed immediately above the assertion that demonstrates the pattern, so the agent has a live example to reference.

**Why it is a good example:** The use of `@dev @architect` (multi-role addressing) is the most structured form of the pattern. The author is routing the same observation to two different roles for different actions — documentation vs. standards adoption. This shows the pattern can carry routing metadata, not just content.

---

### Example 5 — Cross-System Reference (OSBot-Utils missing capability)

**File:** `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Upload.py`, line 264

**Comment text:**
```python
# @dev : capture this missing method in OSBot-Utils (at the moment the processes helper class only has a method that hands the execution until the process is completed
```

**What it communicates:** While writing `debug__start_and_stop_server_using_port`, Dinis discovered that `OSBot-Utils`'s process helper class lacks a non-blocking `Popen`-style wrapper. He had to fall back to `subprocess.Popen` directly. The comment identifies an upstream library gap that the Developer should file as an issue or contribution to the `OSBot-Utils` repo — this is a cross-repository action item, not just a local refactor.

**Why it is a good example:** This comment crosses system boundaries. It does not describe a problem in _this_ codebase — it describes a gap in a dependency. Without the inline annotation, this observation would be lost. The pattern works here because the developer is in flow, has just discovered the gap, and captures it at the point of discovery.

---

## C. Observations & Architectural Notes

### API Layer

- `Fast_API__QA__Server` (`sg_send_qa/api/Fast_API__QA__Server.py`) has no tests targeting it directly and no local start command. The module-level `todo:` on line 66 is a dangling comment (blank `# todo:` with no content).
- `routes__download.py` routes contain logic they should not — routes should be thin dispatchers only.
- `Fast_API__Test_Objs__QA` (`sg_send_qa/api/test_utils/`) exists but has no test coverage.

### Browser Harness

- `SG_Send__Browser__Test_Harness` does too much — API server lifecycle, UI server lifecycle, browser creation, state persistence, token injection should each be a separate concern.
- The attribute `sg_send` inside the harness is a misleading name; it holds a `SG_Send__Browser__Pages` instance (page abstraction), not a service connection.
- `SG_Send__Browser__Pages` has page-specific logic (`extract__download_page`) that does not belong in a generic pages class.
- `Safe_UInt__Port` throws `ValueError` for `None` even when the value is set in the constructor call — a Type_Safe primitive bug to investigate.
- The Playwright Sync API inside asyncio loop error (seen in `test_debug_inner_calls_of_setup`) is a fundamental issue — it prevents keeping the browser open across multiple test class executions, which would be a significant performance win.

### Test Utilities

- `ScreenshotCapture` (`sg_send_qa/utils/QA_Screenshot_Capture.py`) should be a Type_Safe class, should be named `QA_Screenshot_Capture` to match the filename, and should not perform side-effects (`mkdir`) in `__init__`.
- `_upload_with_simple_token` helper lives inside a test class (`test_Friendly_Token`) but it belongs in a dedicated Upload Page class. Its presence in the test class creates maintenance duplication.
- Screenshot capture calls appear as `shots.capture(self.sg_send.raw_page(), ...)` throughout — the `self.sg_send.raw_page()` repetition is LLM and human context tax and should be encapsulated.
- Screenshot metadata description should be LLM-generated from code + screenshots, not manually provided in the test.

### State Management / Schemas

- `Schema__Harness_State` (`sg_send_qa/browser/Schema__Harness_State.py`) uses plain `int` and `str` fields — these should be Type_Safe primitives (e.g., `Safe_UInt__Port`, typed path).
- `State_Machine__Utils.to_mermaid()` and `export_schemas._machine_payload()` both use raw string construction for Mermaid output — should use MGraph_DB.
- `export_schemas.py` top-level functions should be instance methods on a class.
- `QA_Types.py` defines multiple data classes in a single file — each should live in its own file.
- `QA_Config.py` has a manual field-by-field JSON deserialisation that should be replaced by Type_Safe's native loading.

### CI / Infrastructure

- The CLI (`sg_send_qa/cli/run_tests.py`) currently only runs the entire test suite with no granularity. It needs: per-test execution, http vs. browser modes, a plan for CLI capability.

---

## D. Refactoring Backlog

| ID | File(s) | Comment | Recommended Action |
|----|---------|---------|-------------------|
| REFACTOR-001 | `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py` | "split this class into smaller parts/concerns... already doing too much; rename sg_send" | Extract API lifecycle, UI lifecycle, state persistence each into separate classes. Rename `sg_send` attribute to `pages` or `browser_pages`. |
| REFACTOR-002 | `sg_send_qa/browser/JS_Query__Execute.py` | "refactor this into a separate class (focused only on LocalStorage)" | Extract `JS_Query__LocalStorage` class from `storage_*` methods. |
| REFACTOR-003 | `sg_send_qa/browser/JS_Query__Execute.py` | "refactor this into a separate class" (light DOM reads) | Extract `JS_Query__LightDOM` class from `light_*` methods. |
| REFACTOR-004 | `sg_send_qa/browser/JS_Query__Execute.py` | "refactor this into a separate class" (predicates) | Extract `JS_Query__Predicates` class from `predicate__*` methods. |
| REFACTOR-005 | `sg_send_qa/browser/SG_Send__Browser__Pages.py` | "this logic should not be here (inside this generic SG_Send__Browser__Pages class)" | Move `extract__download_page()` and similar page-specific methods to dedicated page classes. |
| REFACTOR-006 | `sg_send_qa/browser/Schema__Harness_State.py` | "refactor all types below to be Type_Safe primitives" | Replace `int` port fields with `Safe_UInt__Port`, `str` path fields with typed path primitives. |
| REFACTOR-007 | `sg_send_qa/state_machines/export_schemas.py` | "refactor these into instance methods; replace path and data with Type_Safe primitives" | Wrap module-level functions in a class; replace raw `Path` / `dict` with typed primitives. |
| REFACTOR-008 | `sg_send_qa/state_machines/export_schemas.py` and `State_Machine__Utils.py` | "refactor mermaid code to use MGraph_DB" (appears in two files) | Replace string-building Mermaid generation with MGraph_DB rendering. |
| REFACTOR-009 | `sg_send_qa/models/QA_Types.py` | "refactor out each class into a separate file; convert str into Type_Safe classes" | One file per data class. Replace bare `str` with Type_Safe str primitives. |
| REFACTOR-010 | `sg_send_qa/models/QA_Config.py` | "separate to individual classes; refactor logic to leverage Type_Safe" | Simplify the manual JSON deserialisation using Type_Safe native loading. |
| REFACTOR-011 | `sg_send_qa/utils/QA_Screenshot_Capture.py` | "refactor to Type_Safe class (name should be Screenshot_Capture... should not do anything that changes state in __init__)" | Convert to Type_Safe. Move `mkdir` call out of `__init__`. Rename to match filename. |
| REFACTOR-012 | `sg_send_qa/cli/run_tests.py` | "refactor to a) have a lot more granularity b) support individual test execution c) provide http and browser based execution" | Redesign CLI with subcommands. Plan capability set before implementation. |
| REFACTOR-013 | `sg_send_qa/cli/QA_Generate_Docs.py` | "we should be using Type_Safe here; tests_dir is hardcoded; fix comments location; reimport using OSbot_Git; reimplement using Type_Safe schemas" | Multiple issues in one file — address as a single dedicated refactor sprint. |
| REFACTOR-014 | `sg_send_qa/server/main.py` | "refactor this into Fast_API__Serverless class" | Align `server/main.py` with the pattern in `sg_send_qa/api/Fast_API__QA__Server.py`. |
| REFACTOR-015 | `tests/qa/v030/p0__friendly_token/test__friendly_token.py` | Multiple: hardcoded path, _GROUP defined inline, set_access_token handling, screenshot call verbosity | Move `_upload_with_simple_token` to an Upload Page class. Remove hardcoded paths. Resolve test name / shots name sync automatically. |
| REFACTOR-016 | `tests/integration/browser/test_SG_Send__Browser__Pages__Upload.py` | "upload__get_friendly_token methods need to be moved to a class with logic specific to this upload page" | Move to Upload Page class (same target as REFACTOR-015). |

---

## E. Performance Investigation Notes

### Full setup() Timing Breakdown

Top-level timing (from `current_logic()` in `Page__Send_SGraph_Ai__Upload`):

| Step | Run 1 | Run 2 | Run 3 |
|------|-------|-------|-------|
| setup harness | 0.000 s | 0.000 s | 0.000 s |
| setup chrome | 0.243 s | 0.320 s | 0.303 s |
| set_access_token | 0.856 s | 0.719 s | 0.678 s |
| open page root | 0.108 s | 0.099 s | 0.093 s |
| **Total** | **~1.207 s** | **~1.138 s** | **~1.074 s** |

Note: "setup chrome" here means connecting to an already-running Chrome process, not launching it. This isolates the harness setup cost.

### Inner Breakdown of setup() (from `debug_inner_calls_of_setup()`)

| Step | Run 1 | Run 2 |
|------|-------|-------|
| _load_saved_state | 0.000 s | 0.000 s |
| _start_api_server | 0.240 s | 0.222 s |
| _build_ui | 0.107 s | 0.103 s |
| _start_ui_server | 0.005 s | 0.003 s |
| _create_browser | 0.000 s | 0.000 s |
| _save_state | 0.000 s | 0.000 s |
| capture_stderr | 0.000 s | 0.000 s |

### Identified Bottlenecks

1. **`_start_api_server` (~230 ms)** — dominated by `setup__send_user_lambda__test_client()` (~120 ms) and `api_server.start()` (~110 ms).
2. **`_build_ui` (~105 ms)** — static file build / copy step.

Inner breakdown of `_start_api_server` (from `debug_inner_methods_of__start_api_server()`):

| Step | Run 1 | Run 2 |
|------|-------|-------|
| setup__send_user_lambda__test_client | 0.115 s | 0.124 s |
| setup Fast_API_Server | 0.000 s | 0.000 s |
| start api server | 0.105 s | 0.103 s |
| stop api server | 0.112 s | 0.114 s |

### Optimization Strategy — Server Pooling

The key insight from the session: the server cost is paid once per _test class_ execution. If the API server can be kept alive across multiple test class executions (by persisting the PID), the ~230 ms is paid once per test _suite_ run instead of once per test _class_.

The same strategy applies to the Chrome process (already implemented in debug mode via CDP port persistence).

**Blocking issue:** The server can only be stopped by the owner of the `Fast_API_Server` object. If the server is started in one test execution, the object is not available to the next execution. Solution: store the PID alongside the port in the harness state file. On next run, check if `pid` is alive and `port` is open; if so, reconnect instead of starting fresh.

### Status: Proof-of-Concept

Commit `17daf799` added `debug__start_and_stop_server_using_port()`, which demonstrates:
- Starting a uvicorn process via `subprocess.Popen` on a random port
- Waiting for the port to open (`wait_for_port`)
- Confirming the server responds to HTTP (`wait_for_http`)
- Capturing the PID
- Killing the process by PID
- Confirming port closure

The PoC is in `Page__Send_SGraph_Ai__Upload` as a debug method (not yet wired into `SG_Send__Browser__Test_Harness`).

---

## F. Tasks for Follow-Up

- [ ] TASK-001: Investigate `Safe_UInt__Port` ValueError for None — even when value is set in constructor call (`SG_Send__Browser__Pages.py` line 29)
- [ ] TASK-002: Investigate Playwright Sync API / asyncio loop conflict in `test_debug_inner_calls_of_setup` — root cause blocks browser reuse across test class executions
- [ ] TASK-003: File issue in OSBot-Utils for missing non-blocking process start method (current `Popen`-based workaround is in `Page__Send_SGraph_Ai__Upload.debug__start_and_stop_server_using_port`)
- [ ] TASK-004: File issue in OSBot-Utils for `Stderr().start()` not returning `self` — makes chaining impossible (currently requires two lines; see commented-out code in `debug__start_and_stop_server_using_port`)
- [ ] TASK-005: File issue in OSBot-Utils for `kill_process()` — should return `True` when process existed and was stopped cleanly, with optional `wait_for_close` parameter
- [ ] TASK-006: Wire server pooling PoC into `SG_Send__Browser__Test_Harness._start_api_server()` — persist PID in `Schema__Harness_State`, reconnect on next run if PID/port still alive
- [ ] TASK-007: Review branch `origin/claude/create-qa-explorer-team-Tg5A6` — diff vs. dev, extract any needed content, then delete the branch (noted by Dinis in `test_Page__Send_SGraph_Ai__Upload.py` end-of-file comment)
- [ ] TASK-008: Review branch `origin/claude/qa-site-v030-integration-Tg5A6` — assess for deletion (noted by Dinis in same file)
- [ ] TASK-009: Add tests targeting `Fast_API__QA__Server` directly (no coverage currently)
- [ ] TASK-010: Add tests for `Fast_API__Test_Objs__QA` (class exists but untested)
- [ ] TASK-011: Add direct tests for `routes__download.py` routes
- [ ] TASK-012: Move `_upload_with_simple_token` logic out of `test_Friendly_Token` into a dedicated Upload Page class (prerequisite for REFACTOR-001 and REFACTOR-015)
- [ ] TASK-013: Implement screenshot metadata auto-generation via LLM (replace manual `method_doc` in `_shots()` calls)
- [ ] TASK-014: Resolve `QA_Generate_Docs.py` hardcoded `tests_dir` path to account for v031 and later test folders
- [ ] TASK-015: Evaluate whether `sg_send_qa/__init__.py` meta-todo needs an actual action or can be removed

---

## G. Cross-References

### Brief

`team/humans/dinis_cruz/briefs/04/01/v0.19.7__brief__offline-mode-local-llms.md`

### Commits (session: 2026-03-31)

| Hash | Description |
|------|-------------|
| `b34a9117` | started adding comments to source code |
| `c7cc9758` | added more comments |
| `14b05afe` | started refactoring of Page__Send_SGraph_Ai__Upload |
| `16277f19` | start to zoom in on the performance of SG_Send__Browser__Test_Harness |
| `882df1ed` | found first optimisation target |
| `17daf799` | added debug__start_and_stop_server_using_port |

(Commits `aaa1f669` and `4f0945117` are merge commits from earlier work, not part of this annotation session.)

### Files Modified by This Harvest

Source files with comments removed:

- `sg_send_qa/__init__.py`
- `sg_send_qa/server/main.py`
- `sg_send_qa/api/Fast_API__QA__Server.py`
- `sg_send_qa/api/test_utils/Fast_API__Test_Objs__QA.py`
- `sg_send_qa/api/routes/routes__download.py`
- `sg_send_qa/browser/JS_Query__Execute.py`
- `sg_send_qa/browser/SG_Send__Browser__Pages.py`
- `sg_send_qa/browser/SG_Send__Browser__Test_Harness.py`
- `sg_send_qa/browser/Schema__Harness_State.py`
- `sg_send_qa/ci/QA_Diff_Screenshots.py`
- `sg_send_qa/state_machines/State_Machine__Snapshot.py`
- `sg_send_qa/state_machines/export_schemas.py`
- `sg_send_qa/state_machines/State_Machine__Utils.py`
- `sg_send_qa/models/QA_Types.py`
- `sg_send_qa/models/QA_Config.py`
- `sg_send_qa/cli/run_tests.py`
- `sg_send_qa/cli/QA_Generate_Docs.py`
- `sg_send_qa/utils/QA_Screenshot_Capture.py`
- `sg_send_qa/apis_for_sites/send_sgraph_ai/pages/Page__Send_SGraph_Ai__Upload.py`
- `tests/integration/browser/test_SG_Send__Browser__Pages__Upload.py`
- `tests/qa/apis_for_sites/send_sgraph_ai/pages/test_Page__Send_SGraph_Ai__Upload.py`
- `tests/qa/v030/p0__friendly_token/test__friendly_token.py`

---

*Librarian harvest — SG/Send QA v0.19.7 session — 2026-04-01*
