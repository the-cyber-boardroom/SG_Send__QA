# Architect Brief: Browser Persistence Session
**Date:** 2026-04-08
**Source commits:** 0f12d11..61e6602 (origin/dc_offline_development)
**Extracted by:** Architect role

---

## The Architecture Change

### Before (as-was)

The harness managed all infrastructure in a single class (`SG_Send__Browser__Test_Harness`) using in-process, thread-based components:

- **API server:** `Fast_API_Server` started inside the test process via `threading.Thread`. The server lived and died with the test run. Reuse between runs was attempted by detecting an open port and skipping `start()` — but this was brittle because `api_server_port_open()` had a bug (wrong argument order to `port_is_open`).
- **UI (static) server:** `Temp_Web_Server` — started inside the test process, on a randomly assigned or saved port.
- **Browser:** `SG_Send__Playwright_Browser__Chrome` created on every test class instantiation, calling `chromium_executable_path()` which started and stopped a full `sync_playwright` context just to read the binary path. Cost: ~370ms per call.
- **State persistence:** `Harness_State__Persistence` saved port numbers to a temp-folder JSON file, allowing the next run to reconnect if servers were still alive.
- **Overall initialisation cost:** ~1.5 seconds on first run; repeated runs were faster but unreliable due to the port-reuse bug.

No dedicated abstraction existed for "a named local server with lifecycle". All server logic lived inline in `_start_api_server`, `_build_ui`, `_start_ui_server` private methods on the harness.

### After (as-is)

Three new layers manage persistence:

1. **`QA__Local_Servers`** — A filesystem coordination layer. Stores per-server JSON config files under `.local-servers/server-configs/`. Each file holds the PID, port, health check results, and run state. The folder is `.gitignore`d. This class handles all CRUD for those config files via `server_config__load`, `server_config__save`, `server_config__delete`.

2. **`Server__Base__Local` + subclasses** — A base class for all subprocess-managed local servers. Handles:
   - PID tracking and OS-level liveness check (`os.kill(pid, 0)`)
   - Port health check
   - `subprocess.Popen` with `stderr=DEVNULL, stdout=DEVNULL, preexec_fn=os.setsid`
   - Wait-for-port and wait-for-service before returning `True`
   - `server__start()` is idempotent: checks `server__online` first, only spawns a new process if not running
   - Two concrete subclasses: `Server__Base__Local__Fast_API` (uvicorn via `poetry run`) and `Server__Base__Local__Static` (Python's `http.server`)
   - Two thin server subclasses: `Server__API__Send_SGraph_AI` (port 50001, FastAPI) and `Server__Http__Send_SGraph_AI` (port 50002, static files)

3. **`QA__Local_Browser`** — Caches the Chromium executable path in `.local-servers/browser-config.json`. The path is resolved once (paying the ~370ms `sync_playwright().start()` cost) and then read from disk on all subsequent calls. `SG_Send__Playwright_Browser__Chrome` now calls `QA__Local_Browser().chromium_executable_path()` instead of calling `chromium_executable_path()` inline.

4. **`QA_Browser` module-level singletons** — Two module globals (`_qa_browser`, `_qa_browser__headless`) lazily create and hold `QA_Browser` instances with their Playwright context and CDP connection alive. `SG_Send__Browser__Pages.qa_browser()` returns these singletons instead of creating a new `QA_Browser` per test class. This eliminates the ~225ms Playwright context startup and ~390ms CDP connection cost on all runs after the first.

**`SG_Send__Browser__Test_Harness` changes:**
- `_start_api_server` renamed to `start_api_server` (public, delegates to `Server__API__Send_SGraph_AI.server__start()`)
- `_build_ui` renamed to `build_ui`; `_ui_content_hash` renamed to `ui_content_hash` and reimplemented to use `version__sgraph_ai_app_send` string MD5 instead of walking the filesystem
- `_start_ui_server` renamed to `start_ui_server`, now delegates to `Server__Http__Send_SGraph_AI.server__start()`
- `_create_browser` renamed to `create_browser`
- `ui_server` (Temp_Web_Server) field removed; replaced by `ui_server__port` (Safe_UInt__Port) — the harness no longer owns the UI server lifetime
- `api_server` (Fast_API_Server) field kept but orphaned — it is set to `None` and not used in the new flow
- `teardown()` no longer stops the API or UI server (they are expected to persist)

**Measured result:** setup cost on the 2nd+ run: ~31ms (servers already running, browser already connected).

---

## Key Design Decisions

### 1. Subprocess vs In-Process API Server

**What was chosen:** `subprocess.Popen` via `poetry run uvicorn`. The server runs as a separate OS process, independent of the Python test process.

**What was tried and rejected:** `Fast_API_Server` (which uses `threading.Thread` internally). The root cause of the original ~1.5s startup was confirmed in commit `7f29d1c`: `Fast_API_Server.start()` ties the server lifetime to the current thread. Restarting the test process kills the server. There is no way to reconnect to a thread-based server across process boundaries.

**Why this was the right choice:** A subprocess survives test process restarts. `server__start()` checks if the port is already open and if the PID is still alive; if both are true, it returns immediately. This is the foundational performance gain.

**Explicit note from Dinis (commit 7f29d1c):** `"@librarian @architect, for future reference, this (wiring the subprocess.Popen) was the most important task from my last offline session, and that should have been the first thing that should had been implemented by the QA team since that is the performance force multiplier"`

### 2. Singleton Pattern for Browser Persistence

**What was chosen:** Module-level globals `_qa_browser` and `_qa_browser__headless` in `QA_Browser.py`. Created lazily on first access; the Playwright context and CDP connection are kept open in the global.

**What was tried and rejected:** Creating a new `QA_Browser` per test class, which paid two costs every time:
- ~225ms to start a `PlaywrightContextManager`
- ~390ms to call `browser_via_cdp` to connect to the running Chromium process

The session confirmed (commit `9a2c4eb`) that these two costs are inside the Playwright library and cannot be reduced from the outside — they must be paid once and amortised.

**Constraint discovered:** `PlaywrightContextManager().start()` cannot be called twice in the same process without triggering `"playwright._impl._errors.Error: It looks like you are using Playwright Sync API inside the asyncio loop"`. This means the singleton pattern is mandatory, not optional, once persistence is the goal.

**Why this was the right choice:** Eliminates ~615ms of reconnect overhead on every test run after the first.

### 3. QA__Local_Servers as the Coordination Layer

**What was chosen:** A single class that owns the `.local-servers/` folder structure. All server configs and browser config are stored here. The folder is relative to `sg_send_qa.path`, so it lives next to the package root in the repo tree but is `.gitignore`d.

**Why this was the right choice:** Decouples "where state is stored" from "which server uses it". Every server class gets a `qa_local_servers: QA__Local_Servers` field and delegates all file I/O through it. Makes it easy to redirect state to a temp folder in tests.

### 4. Chromium Executable Path Caching

**What was chosen:** `QA__Local_Browser` reads and writes `.local-servers/browser-config.json`. If the file exists, the path is read from it (essentially free). If not, `chromium_executable_path()` is called once to populate it.

**What was tried and rejected:** Calling `chromium_executable_path()` inline in `SG_Send__Playwright_Browser__Chrome.__init__`. Profiling in commit `38d77d3` showed this takes ~370ms per call: it starts and stops a full `sync_playwright()` context just to read a file path that never changes.

**Why this was the right choice:** The Chromium binary path is stable. Caching it costs one disk read after the first run.

### 5. UI Content Hash Based on App Version

**What was chosen:** `ui_content_hash()` now returns `str_md5(version__sgraph_ai_app_send)[:8]` — a hash of the SG/Send app version string.

**What was rejected:** Walking the UI source directory and hashing file paths + modification times (the original `_ui_content_hash` implementation).

**Why this was the right choice:** Every merged commit to SG/Send increments its version string. The original filesystem walk was expensive and computing it twice per setup (once for the cache check, once for saving state). The version string achieves the same invalidation with constant cost.

### 6. Base Class Extraction (Server__Base__Local)

**What was chosen:** Claude (AI) performed the refactoring in commit `28e89cb` — extracting `Server__Base__Local`, `Server__Base__Local__Fast_API`, and `Server__Base__Local__Static` from the monolithic `Server__API__Send_SGraph_AI` class.

**Note from Dinis:** `"@dev note that we lost some static config vars what need to be added back and put on a config class"` — this refactoring was fast but incomplete; some constants from the original class were not migrated.

---

## @Architect Tagged Items

The `git diff` search for `@Architect` tags in the commit range returned only the table row from the dev brief itself (not inline code comments). The `@librarian @architect` composite tag in commit `7f29d1c` is the closest to a direct Architect-addressed message:

| Commit | File | Text |
|--------|------|------|
| `7f29d1c` | `test_Page__Send_SGraph_Ai__Upload.py` | `"@librarian @architect, for future reference, this (wiring the subprocess.Popen) was the most important task from my last offline session, and that should have been the first thing that should had been implemented by the QA team since that is the performance force multiplier"` |

---

## Breaking Changes

| Component | What Changed | Previous Behaviour | New Behaviour | Migration Needed |
|-----------|-------------|-------------------|---------------|-----------------|
| `SG_Send__Browser__Test_Harness.api_url()` | Port source changed | Read from `self.api_server.port` (Fast_API_Server attribute) | Read from `self.api_server__port` (Safe_UInt__Port field set by `start_api_server`) | Any code calling `harness.api_server.port` must use `harness.api_server__port` |
| `SG_Send__Browser__Test_Harness.ui_url()` | Port source changed | Read from `self.ui_server.port` (Temp_Web_Server attribute) | Read from `self.ui_server__port` (Safe_UInt__Port field set by `start_ui_server`) | Any code calling `harness.ui_server.port` must use `harness.ui_server__port` |
| `SG_Send__Browser__Test_Harness.teardown()` | Servers not stopped | Stopped API server and UI server | Does not stop API or UI servers (they persist) | Tests that expect servers to be stopped on teardown will now leave servers running |
| `SG_Send__Browser__Test_Harness` class | `ui_server` field removed (commented out) | `ui_server: Temp_Web_Server` was accessible | Field is commented out | Any code referencing `harness.ui_server` will fail |
| `Schema__Harness_State` | Default values changed from `0`/`''` to `None` | `api_port`, `ui_port`, etc. defaulted to `0` or `''` | All fields default to `None` | Logic checking `if state.api_port:` continues to work; logic checking `if state.api_port == 0:` will break |
| `SG_Send__Browser__Test_Harness.access_token()` | Returns random GUID | Returned `self.test_objs.access_token` | Returns `Random_Guid()` — a fresh random value | Tests that compare access tokens to a known value from `test_objs` will fail |
| `SG_Send__Browser__Test_Harness._start_api_server` | Renamed to `start_api_server` | Private method `_start_api_server` | Public method `start_api_server`, different implementation | Any test directly calling `harness._start_api_server()` must be updated |
| `SG_Send__Browser__Test_Harness._build_ui` | Renamed to `build_ui` | Private method `_build_ui` | Public method `build_ui` | Same as above |
| `SG_Send__Browser__Test_Harness._start_ui_server` | Renamed to `start_ui_server` | Private method `_start_ui_server` | Public method `start_ui_server` | Same as above |
| `SG_Send__Browser__Test_Harness._create_browser` | Renamed to `create_browser` | Private method `_create_browser` | Public method `create_browser` | Same as above |
| `SG_Send__Browser__Pages.qa_browser()` | Returns module-level singleton | Created a new `QA_Browser` instance per call | Returns `qa_browser()` or `qa_browser__headless()` singleton | Cannot mix headless and non-headless modes in the same process — the second call will reuse whichever singleton was created first |
| `Schema__Server__Local__Config.server__host` | Default value changed | Defaulted to `'localhost'` | Defaults to `'0.0.0.0'` | Required for the static file server subprocess; the FastAPI server may behave differently on `0.0.0.0` vs `localhost` |

---

## Structural Debt Introduced

1. **`api_server` field is orphaned.** `SG_Send__Browser__Test_Harness.api_server: Fast_API_Server = None` is still declared but never assigned. The comment on it reads: `"@dev todo: with the new mode to start the api server, do we still need this?"` — the field should be removed or repurposed once the answer is confirmed.

2. **`access_token()` is broken for the subprocess-based server.** The harness now returns `Random_Guid()` with a dead second line `return self.test_objs.access_token`. This means the access token injected into the browser will not match any token the API server knows about. The `test_objs` pattern (in-memory test client) is incompatible with the subprocess model. A new mechanism to retrieve or inject the access token from the live server is required.

3. **`saved_state` flow in `start_ui_server` is fragile.** The method contains an inline `todo: @dev fix this setup workflow`. The `saved_state` object is mutated (`saved_state.ui_port = ...`) inside `start_ui_server`, which is a side effect that the caller does not explicitly expect. This creates ordering dependencies.

4. **`config_class()` override pattern is redundant.** Each server subclass declares `config: SpecificConfigClass` and also overrides `config_class()` to return that same class. These two declarations are coupled — if the field type changes, `config_class()` must be updated separately. A metaclass or property-based approach would be cleaner.

5. **Static config constants lost in refactoring.** Commit `28e89cb` notes: `"@dev note that we lost some static config vars what need to be added back and put on a config class"`. The port, host, scheme, and module path constants that were defined at the top of the original `Server__API__Send_SGraph_AI.py` were not fully migrated. Some are now scattered across schema files; others may be absent.

6. **`Harness_State__Persistence` not yet integrated with `.local-servers/`.** Commit `93211db` noted: `"todo: refactor this to use the '.local-servers' folder used by QA__Local_Servers"`. The old persistence still uses a temp folder (`temp_folder_current()`). Two separate state locations now exist in parallel.

7. **Headless mode in `start_ui_server` is broken.** The new `start_ui_server` always calls `Server__Http__Send_SGraph_AI.server__start()`, which requires a `ui__serve_dir` and `ui__content_hash` in the config. In headless CI mode, `build_ui` creates a `Temp_Folder` and sets `ui_serve_dir`, but `saved_state` is `None` in headless mode — the `start_ui_server` implementation dereferences `saved_state.ui_build_folder` without guarding against `None`.

---

## Open Questions for Architecture Review

1. **Should the API and UI servers persist across test suite runs in CI?** The current design persists them in debug (headless=False) mode. In CI (headless=True), the harness calls `server__start()` on `Server__API__Send_SGraph_AI` but the subprocess model means the server will outlive the test process unless explicitly stopped. Should CI teardown call `server__stop()`?

2. **How is the access token obtained from the subprocess server?** The old model used an in-memory `test_objs.access_token` set at startup. With a subprocess server, the token must be requested via the API or injected by a different mechanism. This is unresolved and currently masked by `Random_Guid()`.

3. **Can headless and non-headless QA_Browser singletons coexist in the same process?** The session found they cannot (async loop error). This means a test suite cannot mix headless and visible-browser tests in the same process. Is this an acceptable constraint for the CI pipeline?

4. **Should `QA__Local_Browser` cache invalidation be tied to Chromium version?** The current implementation caches the executable path forever. If Playwright is updated (new Chromium binary), the cached path will be stale. A version fingerprint in `browser-config.json` would fix this.

5. **Is `Server__Base__Local__Static` binding to `0.0.0.0` the correct default?** The schema default changed from `'localhost'` to `'0.0.0.0'` to fix a binding issue with the static server subprocess. This may expose the static server on all network interfaces in environments where that is undesirable.

6. **Should `Server__Base__Local` use `os.setsid` on all platforms?** The subprocess uses `preexec_fn=os.setsid` to create a new process group, which is not available on Windows. This is not a current blocker (the project targets Linux/macOS) but worth noting if CI moves to Windows runners.

---

## Dependency Map (new/changed)

```
SG_Send__Browser__Test_Harness
    ├── Server__API__Send_SGraph_AI          [NEW — was: inline Fast_API_Server]
    │       └── Server__Base__Local__Fast_API
    │               └── Server__Base__Local
    │                       └── QA__Local_Servers    [NEW]
    │
    ├── Server__Http__Send_SGraph_AI         [NEW — was: inline Temp_Web_Server]
    │       └── Server__Base__Local__Static
    │               └── Server__Base__Local
    │                       └── QA__Local_Servers
    │
    └── SG_Send__Browser__Pages
            └── qa_browser() / qa_browser__headless()   [NEW — module-level singletons]
                    └── QA_Browser
                            └── SG_Send__Playwright_Browser__Chrome
                                    └── QA__Local_Browser    [NEW — was: chromium_executable_path() inline]
                                            └── QA__Local_Servers

QA__Local_Servers (.local-servers/ on disk)
    ├── server-configs/api__send-sgraph-ai.json
    ├── server-configs/http__send-sgraph-ai.json
    └── browser-config.json
```

**Removed runtime dependencies (from harness):**
- `Fast_API_Server` (in-process thread-based server) — no longer started
- `Temp_Web_Server` (in-process static file server) — no longer started
- `Send__User_Lambda__Test_Objs` (in-memory test client for access token) — no longer used in the live path
