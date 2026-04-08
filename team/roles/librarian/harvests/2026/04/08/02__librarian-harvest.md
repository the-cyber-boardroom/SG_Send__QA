# Librarian Harvest: Browser Persistence Session
**Harvest date:** 2026-04-08
**Harvested by:** Librarian (claude/session-debrief-8xeEK)
**Session narrative:** [01__session-narrative.md](./01__session-narrative.md)
**Commit range:** `0f12d11..61e6602` (origin/dc_offline_development)
**Brief:** `team/humans/dinis_cruz/briefs/04/08/v0.20.38__dev-brief__qa-offline-coding-session-workflow.md`

---

## A. Tagged Comments — Extracted and Routed

### @Dev / @dev (routed → [03__dev-brief.md](./03__dev-brief.md))

| # | Location | Comment |
|---|----------|---------|
| 1 | `Page__Send_SGraph_Ai__Upload.py` | `@dev can you refactor this (and others) to Page__Send_SGraph_AI__Browse (since we should be using "AI" not "Ai")` |
| 2 | `Page__Send_SGraph_Ai__Upload.py` | `@dev theis setup feels quite generic and should be moved to a base class that Page__Send_SGraph_Ai__Upload then uses` |
| 3 | `SG_Send__Browser__Pages.py` | `@dev note that at the moment we can't mix headless and non-headless modes, or we get back our async error` |
| 4 | `SG_Send__Browser__Test_Harness.py` | `@dev todo: with the new mode to start the api server, do we still need this? (api_server field)` |
| 5 | `SG_Send__Browser__Test_Harness.py` | `@dev see what we need to do with this saved_state` |
| 6 | `SG_Send__Browser__Test_Harness.py` | `@dev refactor these test_objs for one that works with the local server/process we just started` |
| 7 | `SG_Send__Browser__Test_Harness.py` | `@dev see what refactorings we can do this (also see what we should do with the saved state)` |
| 8 | `SG_Send__Browser__Test_Harness.py` | `@dev fix this setup workflow (since we shouldn't need to have all these checks here), namely around how the saved_sate is wired up` |
| 9 | `SG_Send__Browser__Test_Harness.py` | `@dev following on the comment I left on _ui_content_hash, not only that was not an efficient way to do this, we were calling it twice` |
| 10 | `SG_Send__Browser__Test_Harness.py` | `@dev can you map out the scenario where we add a couple more hashes and version numbers to each UI core manifest (created at build time on CI for the __Send repo)` |
| 11 | `Server__API__Send_SGraph_AI.py` | `@dev use Safe_Id once default value auto-conversion is confirmed` (server_id field) |
| 12 | `Server__API__Send_SGraph_AI.py` | `@dev add checks to make sure all vars valued to safely create the process are correctly set up` |
| 13 | `Server__Http__Send_SGraph_AI.py` | `@dev use Safe_Id once default value auto-conversion is confirmed` (server_id field) |
| 14 | `QA__Local_Servers.py` / constants | `@dev: move to common config location` (SEND_SGRAPH_AI__SERVER__PORT) |
| 15 | `QA__Local_Servers.py` / constants | `@dev: I think an Enum would be better here` (scheme constant) |
| 16 | commit `28e89cb` | `@dev can you review the last commit removals since we lost in the factoring some of these static values and started to use hard-coded primitives variables in the code` |
| 17 | test file | `@dev fix in OSBot_Utils` (ui_folder / ui_server not Type_Safe classes) ×2 |
| 18 | `Schema__Upload_Page` import | `@qa: refactor out this dependency from this class` |
| 19 | test file | `@qa we should have a better way to confirm that all went well` |

### @QA / @qa (routed → [04__qa-brief.md](./04__qa-brief.md))

The `@qa` tags in this session were primarily **teaching annotations** left in commented-out test code, not formal test requirements. They form a dense tutorial on QA patterns and code style. Key themes:

| Theme | Example comment |
|-------|----------------|
| Use `test__init__` pattern | `@qa I think test__init__ is a better name for what this test is doing` |
| Use `.obj()` for assertions | `@qa for classes that implement type safe, instead of doing this which doesn't gives us a lot` |
| Avoid redundant tests | `@qa we don't need to test this here` / `@qa these two are also already tested` |
| Return types on methods | `@qa the problem of not adding return types to methods like this, is that it not obvious what is the class` |
| Formatting & alignment | `@qa note that the code above will be MUCH more readable once it is correctly formatted and aligned` |
| Singleton risk | `@qa all these tests should always run with a live browser — what we want to do is make the process of starting and reusing the browser as effective as possible` |

Full list (15 items) in `04__qa-brief.md`.

### @Librarian
No explicit `@Librarian` tags were found in this commit range. The session's communication was primarily via `@dev` and `@qa` tags plus rich commit messages.

### @Architect (routed → [05__architect-brief.md](./05__architect-brief.md))
No explicit `@Architect` tags found. Architectural decisions were captured in commit messages and inline comments without the `@Architect` prefix. See `05__architect-brief.md` for the full architectural analysis extracted from the narrative.

---

## B. New Patterns & Conventions Introduced

### 1. `sg_send_qa/local_servers/` package
**Introduced:** commit `4a13b01`
**Structure:**
```
sg_send_qa/local_servers/
├── __init__.py
├── QA__Local_Servers.py          ← coordinator: reads/writes .local-servers/*.json
├── QA__Local_Browser.py          ← Chromium path cache
├── Server__Base__Local.py        ← abstract base: start/stop/check lifecycle
├── Server__Base__Local__Fast_API.py  ← FastAPI subprocess mixin
├── Server__Base__Local__Static.py    ← static file server mixin
├── Server__API__Send_SGraph_AI.py    ← concrete: FastAPI on port 50001
├── Server__Http__Send_SGraph_AI.py   ← concrete: static server on port 50002
└── schemas/
    ├── Schema__Server__Local__Config.py
    ├── Schema__Server__Local__Fast_API__Config.py
    ├── Schema__Server__Local__Static__Config.py
    ├── Schema__Server__API__Send_SGraph_AI__Config.py
    └── Schema__Server__Http__Send_SGraph_AI__Config.py
```
**Pattern:** Two-level hierarchy. `Server__Base__Local` defines the contract (`start`, `stop`, `server__configured_ok`, `is_running`). Protocol subclasses add startup mechanics. Concrete classes add identity (port, config file ID).

**Adoption:** All future QA servers should follow this pattern. New servers = new concrete class + new schema.

### 2. `.local-servers/` config-file coordination
**Introduced:** commit `4a13b01` / `1dcc0b7`
**How it works:** `QA__Local_Servers` reads/writes JSON files under `.local-servers/` (project root, git-ignored). Each server writes `{server_id}.json` with its PID and port. On next run, the coordinator checks if the PID is alive and the port is open — if yes, reuse; if no, restart.

**Key invariant:** Config files are the source of truth for "is this server running?" not in-memory state. This survives Python process restarts.

### 3. Module-level singletons in `QA_Browser`
**Introduced:** commit `751ddb6`
**How it works:** Two module globals (`_qa_browser`, `_qa_browser__headless`) hold `SG_Send__Playwright_Browser__Chrome` instances. `qa_browser()` returns the singleton, creating it only once per process.

**Why it matters:** `sync_playwright().start()` costs ~374ms. `browser_via_cdp` costs ~395ms. Both paid once per process instead of once per test class.

**Constraint noted by Dinis:** Cannot mix headless and non-headless modes in the same process (noted in `@dev` comment on `qa_browser()`).

### 4. Chromium path caching via `QA__Local_Browser`
**Introduced:** commit `9a2c4eb`
**How it works:** First run resolves the Chromium executable path and writes it to `.local-servers/browser-config.json`. Subsequent runs read from cache, skipping the `sync_playwright().start()` call (~374ms).

### 5. Naming convention: `"AI"` not `"Ai"` in class names
**Noted by Dinis:** `@dev can you refactor this (and others) to Page__Send_SGraph_AI__Browse (since we should be using "AI" not "Ai")`
**Action needed:** All `Page__Send_SGraph_Ai__*` classes should be renamed to `Page__Send_SGraph_AI__*`.

---

## C. Architectural Decisions (for the record)

See [05__architect-brief.md](./05__architect-brief.md) for full analysis. Summary:

1. **Subprocess over threading** — `Fast_API_Server` threads die with the Python process. `subprocess.Popen` via `poetry run uvicorn` survives. This was the foundational insight (commit `7f29d1c`).
2. **Config files over in-memory state** — persistence across process restarts requires external state. `.local-servers/*.json` is the chosen mechanism.
3. **Singletons at module level** — browser connections are expensive to create; module globals ensure they are shared across all test class instantiations within a process.

---

## D. Temporary vs Permanent

| Item | Type | Location | Action |
|------|------|----------|--------|
| `debug_*` methods in `Page__Send_SGraph_Ai__Upload` | Temporary scaffolding | `sg_send_qa/apis_for_sites/.../Page__Send_SGraph_Ai__Upload.py` | Remove or move to a dedicated debug module |
| `print_duration` calls throughout harness | Temporary measurement | `SG_Send__Browser__Test_Harness.py` | Remove from production path |
| Commented-out `test_Page__Send_SGraph_Ai__Upload__Unit` methods | Teaching annotations | `tests/qa/.../test_Page__Send_SGraph_Ai__Upload.py` | Remove once team has absorbed the patterns |
| `for__osbot_playwright/chromium_executable_path.py` | Unclear — workaround? | `sg_send_qa/browser/for__osbot_playwright/` | Review: is this needed long-term or a temp shim? |
| `tests/qa/local_servers/schemas/safe_str/Safe_Str__Python__FastAPI_Handler.py` | **Should not be in tests/** | `tests/qa/local_servers/schemas/safe_str/` | Move to `sg_send_qa/` — currently breaks package install (P0 from QA brief) |
| `Server__API__Send_SGraph_AI`, `QA__Local_Servers`, `QA__Local_Browser` | **Permanent** | `sg_send_qa/local_servers/` | Core infrastructure — keep and extend |
| Schema classes under `sg_send_qa/local_servers/schemas/` | **Permanent** | as above | Core configuration — keep |

---

## E. Knowledge Gaps & Open Questions

1. **`api_server` field in `SG_Send__Browser__Test_Harness`** — `@dev` tag asks: do we still need this with the new subprocess model? Unresolved.
2. **`saved_state` wiring** — Multiple `@dev` notes flag that the saved_state integration is awkward now that the subprocess model owns server persistence. The harness and local_servers are partially overlapping in responsibility.
3. **Headless + non-headless singleton conflict** — Explicitly noted but not resolved. The two singletons (`_qa_browser` / `_qa_browser__headless`) mitigate this but the constraint is undocumented for future developers.
4. **Static config constants lost in refactor** — commit `28e89cb` message explicitly flags that some constants were lost during the Claude-assisted refactor. Which ones and where they should live is not documented.
5. **`Schema__Server__Local__Fast_API__Config` imports `Safe_Str__Python__FastAPI_Handler` from `tests/`** — This breaks package installation. Immediate fix needed (see `04__qa-brief.md` RISK-1).
6. **UI version hash strategy** — `@dev` asks about adding multiple hashes to the UI manifest at CI build time in the `__Send` repo. The full design is not yet defined.
7. **Performance on first run vs subsequent runs** — The ~36ms target is for subsequent runs only. First-run cost (server startup, browser connection) is not yet documented in a test.

---

## F. Cross-References

| Document | Path |
|----------|------|
| Session brief | `team/humans/dinis_cruz/briefs/04/08/v0.20.38__dev-brief__qa-offline-coding-session-workflow.md` |
| Previous harvest | `team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md` |
| Session narrative | `team/roles/librarian/harvests/2026/04/08/01__session-narrative.md` |
| Dev brief | `team/roles/librarian/harvests/2026/04/08/03__dev-brief.md` |
| QA brief | `team/roles/librarian/harvests/2026/04/08/04__qa-brief.md` |
| Architect brief | `team/roles/librarian/harvests/2026/04/08/05__architect-brief.md` |

**New files added this session** (39 total — see `git diff --name-status 0f12d11..61e6602 | grep ^A` for full list):
- Core: `sg_send_qa/local_servers/` (14 files)
- Tests: `tests/qa/local_servers/` (10 files)
- Pages: `Page__Send_SGraph_Ai__Browse/Download/Gallery.py` + tests
- Browser: `for__osbot_playwright/chromium_executable_path.py`, `QA__Local_Browser.py`

---

## G. Processing State

| Field | Value |
|-------|-------|
| **Last processed commit** | `61e6602` (minor fix — 2026-04-08) |
| **First commit of this range** | `1ff0cae` (started offline session — 2026-04-05) |
| **Total commits processed** | 18 Dinis commits + 8 dev-branch merges |
| **Processed by** | Librarian (claude/session-debrief-8xeEK), 2026-04-08 |
| **Next session: start from** | `61e6602` |

---

*Librarian harvest — SG/Send QA dc_offline_development session — 2026-04-08*
