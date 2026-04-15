# Session Narrative: Browser Persistence & Performance
**Date:** 2026-04-08
**Branch:** origin/dc_offline_development
**Commit range:** 0f12d11..61e6602 (18 Dinis commits, from Sun 5 Apr to Wed 8 Apr 2026)
**Brief:** `team/humans/dinis_cruz/briefs/04/08/v0.20.38__dev-brief__qa-offline-coding-session-workflow.md`

---

## The Problem Being Solved

Before this session, every time a test ran, the test setup (`SG_Send__Browser__Test_Harness.setup()`) had to:
1. Start a FastAPI server using `Fast_API_Server` — via a threading model tied to the current process
2. Build the SG/Send UI static files into a temp folder
3. Start a static file web server
4. Launch Chromium
5. Connect Playwright to Chromium

The total cost: ~1.5 seconds per setup. For a test suite that creates and tears down harnesses per test class, this made interactive development painful. The cost was paid every run with no reuse between executions.

The session's goal: persist these processes outside the Python test runner so they survive across test re-runs. The key insight (from Dinis's previous session, referenced explicitly in commit `7f29d1c`): the API server must run as a **subprocess**, not a thread. A threaded server dies when the Python process exits. A subprocess does not.

---

## Act 1: Observation and Comment (commits 1ff0cae, 6ef691d, 4db9ac5 — Sun 5 Apr, 12:28–13:43)

Dinis started by annotating the existing test class `test_Page__Send_SGraph_Ai__Upload` with a dense set of `@qa`-tagged teaching comments. The code was already working but Dinis was narrating its flaws for the team.

**Key observations made in code (commit 1ff0cae):**
- `sg_send = None` in `Page__Send_SGraph_Ai__Upload` was typed without a type annotation — flagged as a violation of the Type_Safe convention. The reason it had no type: circular dependency with `SG_Send__Browser__Pages`. Dinis noted this is a useful signal: "not being able to use a type here is a good way to detect a problem."
- The existing test class `test_Page__Send_SGraph_Ai__Upload__Unit` had individual tests for each method (`test_has_setup_method`, `test_is_type_safe_subclass`, etc.) — Dinis commented all of these out, explaining they are redundant: a single `test__init__` using `_.obj()` confirms all defaults in one assertion, and later integration tests will exercise all methods by using them.
- Comment pattern introduced: `with Page__Send_SGraph_Ai__Upload() as _:` — the `_` variable convention makes code easier to read at a glance.

**Commit 6ef691d** collapsed the two test classes (`test_Page__Send_SGraph_Ai__Upload__Unit` and `test_Page__Send_SGraph_Ai__Upload`) into one, following the rule: one class per file. All the old Unit tests were moved into the single class. The `teardown()` method had its return value improved: now returns `True` when it actually cleaned up, `False` when no harness was present. Dinis added `assert _.teardown() is False` to `test__init__` to cover this directly.

**Commit 4db9ac5** expanded `test_setup_and_teardown_headless` into a comprehensive state-inspection test, using `_.obj()` and `__()` throughout to assert the deep object graph after `setup()`. Notable:
- Uncovered a `RecursionError` when calling `_.obj()` on the full `Page__Send_SGraph_Ai__Upload` object — attributed to circular dependencies in the object graph.
- `_.harness.api_server.obj()` also caused recursion.
- Workaround: inspect sub-objects individually (`_.harness.config.obj()`, `_.harness.sg_send.obj()`, etc.).
- Timing assertions added: `assert duration__setup.seconds < 2` and `assert duration__teardown.seconds < 0.5`.
- Noted: DevTools websocket message appearing in console output — should be captured by stderr capture, but was not.

---

## Act 2: Root Cause Found (commits 3cedab1, 7f29d1c — Sun 5 Apr, 14:21–14:43)

**Commit 3cedab1** fixed a real bug: `api_server_port_open()` in `SG_Send__Browser__Test_Harness` was calling `port_is_open('localhost', port)` — but the actual signature of `port_is_open` is `def port_is_open(port: int, host='0.0.0.0', timeout=1.0)`. The positional argument order was wrong, so `'localhost'` was being passed as `port` and the actual port number as `host`. This meant the port-reuse check always returned False, causing the API server to restart every single time even when it was already running on the correct port. Fix: changed to keyword arguments — `port_is_open(host='localhost', port=port)`.

The commit also introduced a scratch test class `test_abc` with `test_setup_and_teardown_headless__false` to observe a strange PyCharm behaviour: when a subprocess was started by one test class, it would stay alive after exit, but when a second test class started, the orphaned process would be terminated. Dinis captured this as a `@qa` and `@dev` comment for investigation.

**Commit 7f29d1c** identified the deeper architectural problem. Using `test_star_process` in `test_Debug_weird_process_Recycle`, Dinis confirmed that `_start_api_server` used `Fast_API_Server`, which internally uses `threading.Thread`. Code quoted directly in the comment:

```python
def start(self):
    self.server = Server(config=self.config)
    def run():
        self.server.run()
    self.thread = threading.Thread(target=run)
    self.thread.start()
    wait_for_port(host=FAST_API__HOST, port=self.port)
    self.running = True
    return True
```

The verdict, committed as `@librarian @architect` comment: "this (wiring the subprocess.Popen) was the most important task from my last offline session, and that should have been the first thing that should had been implemented by the QA team since that is the performance force multiplier."

The decision: create a new class `Server__API__Send_SGraph_AI` that uses `subprocess.Popen` and persists its PID to disk so subsequent runs can detect the already-running server and skip the start.

---

## Act 3: New Architecture (commits 4a13b01, 1dcc0b7, 8efdfd5, 1b9bf45 — Mon 6 Apr, 14:45–17:14)

**Commit 4a13b01** introduced three new structures simultaneously:

1. **`sg_send_qa/local_servers/Server__API__Send_SGraph_AI.py`** — a new class that starts the SG/Send FastAPI server as a `subprocess.Popen` call using `poetry run uvicorn`. Key constants defined at module level: `SEND_SGRAPH_AI__SERVER__PORT = Safe_UInt__Port(50001)` (fixed port — noted `@dev: move to common config location`), `SEND_SGRAPH_AI__SERVER__MODULE` derived from the actual `run` function's `__module__` attribute. The `Schema__Server__API__Send_SGraph_AI__Config` schema captures the full server state: PID, port, health check results, timestamps.

2. **`sg_send_qa/local_servers/QA__Local_Servers.py`** — a config persistence manager. Stores per-server JSON config files in `.local-servers/server-configs/{server_id}.json` relative to the QA package root. Methods: `server_config__load`, `server_config__save`, `server_config__exists`, `server_config__delete`. Uses `sg_send_qa.path` (package `__init__.py` now exports `path = __path__[0]`) as the base, so location is always deterministic.

3. **`.local-servers/server-configs/api__send-sgraph-ai.json`** — the persisted config file for the API server.

**Commit 1dcc0b7** refined both classes. `QA__Local_Servers` gained a configurable `base_folder` field, enabling tests to use an alternative root. The `Server__API__Send_SGraph_AI.server__start()` method was completed: it calls `config__update()` first to check if the server is already running, only starts if `server__online is False`, launches via `subprocess.Popen`, and then calls `wait_for__port__open()` before returning. A separate `server__stop()` was implemented using `stop_process(pid)` followed by `wait_for__port__closed()`. The `.local-servers/` folder was added to `.gitignore` (commit 1b9bf45).

**Commit 8efdfd5** began wiring `Server__API__Send_SGraph_AI` into `SG_Send__Browser__Test_Harness`. The harness gained a new field `server__send_graph_ai__api: Server__API__Send_SGraph_AI` and the old `_start_api_server()` method body was replaced with a call to `_.server__start()`. The old in-memory `Fast_API_Server` code was commented out.

**Commit 1b9bf45** completed the wiring. First test with the new architecture in `test_setup_and_teardown_headless__false` captured the critical timing data:
```
# first time the code executes we get
#           action took: 1.504 seconds
# next execution is :
#           action took: 0.015 seconds
```
The SG/Send API server was now persisting at `http://localhost:50001/info/status` between runs, with state stored in `.local-servers/server-configs/api__send-sgraph-ai.json`.

---

## Act 4: Refactoring and UI Server (commits 93211db, 61750e6, 28e89cb, d68fe29 — Mon–Tue 6–7 Apr)

**Commit 93211db** fixed `build_ui` (renamed from `_build_ui`). The old `_ui_content_hash()` was computing an md5 over all source file paths and modification times — a full filesystem walk. The new `ui_content_hash()` reads `version__sgraph_ai_app_send` (the `__Send` repo's version string) and md5s that. Since every CI commit bumps the version, version change = UI rebuild needed. This removed the filesystem walk entirely. Also: `api_server.port` (the in-memory Fast_API_Server) was replaced by `api_server__port` (a `Safe_UInt__Port` field that stores just the port number, set after `server__start()` returns).

**Commit 61750e6** added a `__init__.py` to `sg_send_qa/local_servers/` and left a comment flagging the next investigation target: `_start_ui_server`.

**Commit 28e89cb** is the major refactoring commit, noted in the commit message as "via Claude". The 185-line `Server__API__Send_SGraph_AI` was collapsed to 16 lines — a thin subclass of a new base class `Server__Base__Local`. Two new files:

- `sg_send_qa/local_servers/Server__Base__Local.py` — common lifecycle for all subprocess-managed local servers: config persistence, PID tracking, port health check, start/stop/wait methods, `subprocess.Popen` with `preexec_fn=os.setsid` for process group management.
- `sg_send_qa/local_servers/schemas/Schema__Server__Local__Config.py` — base config schema.

Also added `Server__Http__Send_SGraph_AI` (the static file server counterpart) as another thin subclass. **Warning from the commit message:** "we lost some static config vars what need to be added back and put on a config class." Several module-level constants (`SEND_SGRAPH_AI__SERVER__PORT`, `SEND_SGRAPH_AI__SERVER__SCHEME`) were previously explicit; after the refactor they were inline or inherited from base defaults.

**Commit d68fe29** wired in `start_ui_server()` (renamed from `_start_ui_server`). The `Temp_Web_Server` was replaced by `Server__Http__Send_SGraph_AI.server__start()`. The server binds to `0.0.0.0` rather than `localhost` — this was needed for the static server (binding to `localhost` was failing; `subprocess.DEVNULL` for stdout/stderr was required rather than `subprocess.PIPE`). `Schema__Harness_State` fields changed from `int = 0` and `str = ''` defaults to `= None` to enable proper null detection. After this commit, the full setup path through `SG_Send__Browser__Test_Harness.setup()` measured approximately **~31ms on second and subsequent runs**:
```python
def setup(self):
    saved_state = self._load_saved_state()
    self.start_api_server(saved_state)    # ~0ms (server already running)
    self.build_ui        (saved_state)    # ~0ms (hash matches, skip rebuild)
    self.start_ui_server(saved_state)     # ~0ms (server already running)
    self._save_state()
```

---

## Act 5: Browser Persistence (commits c0b2a79, 38d77d3, 9a2c4eb, 751ddb6, 61e6602 — Wed 8 Apr, 00:10–14:36)

**Commit c0b2a79** wired in `create_browser()` (renamed from `_create_browser`). The browser setup step itself added ~0ms to the setup timer (it only constructs the object). But opening the first page took ~850ms. Dinis began dissecting this:
- `_.sg_send.qa_browser()` → ~0ms (object creation)
- `_.sg_send.qa_browser().chrome()` → ~0.385s
- `_.sg_send.qa_browser().chrome().page()` → ~0.752s

**Commit 38d77d3** identified a specific bottleneck inside `SG_Send__Playwright_Browser__Chrome.__init__`: every construction called `chromium_executable_path()`, which did:
```python
pw = sync_playwright().start()   # ~ 0.374 seconds
path = pw.chromium.executable_path
pw.stop()                        # ~ 0.004 seconds
```
Starting and stopping a full sync_playwright process just to get the Chromium binary path — and this was called every time an `SG_Send__Playwright_Browser__Chrome` instance was created. The fix: cache this value.

**Commit 9a2c4eb** introduced `QA__Local_Browser` — a new class that caches the Chromium executable path to disk in `.local-servers/browser-config.json`. The `chromium_executable_path()` function was moved to `sg_send_qa/browser/for__osbot_playwright/chromium_executable_path.py` to avoid circular imports. After the refactor:
- `SG_Send__Playwright_Browser__Chrome()` → ~0.004s (was ~0.267s)
- `_.sg_send.qa_browser().chrome()` → ~0.006s (was ~0.385s)

The remaining delay before first page was the Playwright context manager start (~0.211s) and `browser_via_cdp` (~0.392s). Dinis noted these are inside the Playwright codebase — limited optimization available. After connecting, subsequent page opens were ~90ms (404 page) and ~124ms (full root page).

**Commit 751ddb6** added module-level singleton functions in `QA_Browser.py`:
```python
_qa_browser = None
_qa_browser__headless = None

def qa_browser() -> QA_Browser:
    global _qa_browser
    if _qa_browser is None:
        browser = QA_Browser()
        browser.chrome().browser()   # trigger expensive creation and connection
        _qa_browser = browser
    return _qa_browser

def qa_browser__headless() -> QA_Browser:
    ...
```
`SG_Send__Browser__Pages.qa_browser()` was updated to use these singletons instead of creating a new `QA_Browser` per call. The test `test_setup_and_teardown_headless__false__using_singleton__qa_browser` confirmed the complete target performance:
```
# first object
"setup and execution"   → ~ 0.031 seconds
"invoke qa_browser singleton" → ~ 0.571 seconds  (first ever connection)
"open page"             → ~ 0.061 seconds

# subsequent objects (singleton already warm)
"setup and execution"   → ~ 0.036 seconds
"invoke qa_browser singleton" → ~ 0.0 seconds
"open 404 page"         → ~ 0.054 seconds
"open root page"        → ~ 0.084 seconds
```

**Commit 61e6602** was a minor fix: `QA_Browser.open()` now accepts `**kwargs` and passes them through to `page.open()`, enabling callers to pass `wait_for_ready=False`. Also removed a stale `# ← the fix` comment in `SG_Send__Playwright_Browser__Chrome`. The brief (`v0.20.38__dev-brief__qa-offline-coding-session-workflow.md`) was committed in this final commit.

---

## Key Achievement

**Before this session:** ~1.5s per test setup, all costs paid fresh every run.

**After this session (second+ run):**
| Phase | Before | After |
|-------|--------|-------|
| API server start | ~1.35s (thread, dies on exit) | ~0ms (subprocess persists, reused) |
| UI build | ~0.79s (full filesystem hash) | ~0ms (version string hash, cached) |
| UI server start | ~0.1s (Temp_Web_Server) | ~0ms (subprocess persists, reused) |
| Browser connection | ~0.75s (new Playwright context + browser_via_cdp) | ~0ms (singleton reused) |
| **Total setup** | **~3.0s** | **~31ms** |

First run of any session still pays the full cost, after which all processes persist.

---

## What Was Kept vs Discarded

**Permanent additions:**
- `sg_send_qa/local_servers/Server__Base__Local.py` — base class for subprocess-managed servers
- `sg_send_qa/local_servers/Server__Base__Local__Fast_API.py` — FastAPI-specific subclass
- `sg_send_qa/local_servers/Server__API__Send_SGraph_AI.py` — thin SG/Send API server subclass (16 lines)
- `sg_send_qa/local_servers/Server__Http__Send_SGraph_AI.py` — thin HTTP static server subclass
- `sg_send_qa/local_servers/QA__Local_Servers.py` — config persistence manager
- `sg_send_qa/local_servers/QA__Local_Browser.py` — browser config cache (Chromium path)
- `sg_send_qa/browser/QA_Browser.py` — added module-level singleton functions `qa_browser()` and `qa_browser__headless()`
- `sg_send_qa/browser/for__osbot_playwright/chromium_executable_path.py` — moved to avoid circular imports
- `sg_send_qa/local_servers/schemas/Schema__Server__Local__Config.py` — base config schema
- `sg_send_qa/local_servers/schemas/Schema__Server__API__Send_SGraph_AI__Config.py` — API server config schema

**Scaffolding that remains in source but should be cleaned:**
- `test_Debug_weird_process_Recycle` class and its `test_star_process` method — diagnostic test, removed by commit 8efdfd5 but the observation was captured
- `test_abc` class — removed by commit 8efdfd5
- Large blocks of commented-out `obj()` assertions in `test_setup_and_teardown_headless` — will grow very stale as code evolves
- The `@dev` and `@qa` inline comments throughout — knowledge transfer complete, should be cleaned

**Discarded patterns:**
- `Fast_API_Server` (threading model) for the API server — replaced by subprocess
- `Temp_Web_Server` for the UI server — replaced by subprocess
- `_ui_content_hash()` (filesystem walk) — replaced by version string hash
- The `test_Page__Send_SGraph_Ai__Upload__Unit` class — merged into the main test class
