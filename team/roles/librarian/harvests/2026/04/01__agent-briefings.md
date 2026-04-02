# Agent Briefings — dc_offline_dev Harvest

**Source harvest:** `team/roles/librarian/harvests/2026/04/01__dc_offline_dev__comment-harvest.md`
**Briefing date:** 2026-04-02

---

## Developer

The harvest produced a 16-item refactoring backlog and 15 follow-up tasks. Highest priority code changes: extract `JS_Query__LocalStorage`, `JS_Query__LightDOM`, and `JS_Query__Predicates` from `JS_Query__Execute.py` (REFACTOR-002/003/004); move `_upload_with_simple_token` out of the test class into `Page__Send_SGraph_Ai__Upload` (TASK-012 / REFACTOR-015/016); convert `QA_Screenshot_Capture` to a Type_Safe class without `__init__` side-effects (REFACTOR-011); and file OSBot-Utils issues for the missing non-blocking process start method (TASK-003), the `kill_process` return value (TASK-005), and the `Stderr().start()` chaining gap (TASK-004). The server-pooling PoC in `debug__start_and_stop_server_using_port` is a TASK-006 implementation target once the refactoring stabilises.

## QA Lead

Two coverage gaps stand out: `Fast_API__QA__Server` has no direct tests (TASK-009), and `Fast_API__Test_Objs__QA` is entirely untested (TASK-010). The `routes__download.py` routes contain logic rather than thin dispatch, making them untestable at the route layer — this is a blocker for TASK-011. The screenshot description workflow is manual and error-prone; TASK-013 proposes LLM-generated metadata from code and screenshots, which would improve documentation quality and reduce test maintenance burden. The `test_debug_inner_calls_of_setup` skip (Playwright Sync API inside asyncio loop) should be investigated as a root-cause issue (TASK-002) since it blocks browser reuse across test classes — a significant CI speed gain.

## Architect

Six architectural issues require structural decisions before implementation: (1) `SG_Send__Browser__Test_Harness` violates SRP — API lifecycle, UI lifecycle, browser creation, state persistence, and token injection each need their own class (REFACTOR-001); (2) `sg_send` attribute on the harness is a misleading name — should become `pages` or `browser_pages`; (3) `SG_Send__Browser__Pages` contains page-specific logic (`extract__download_page`) that belongs in dedicated page classes (REFACTOR-005); (4) `Schema__Harness_State` uses plain `int`/`str` where Type_Safe primitives (`Safe_UInt__Port`, typed paths) should be used (REFACTOR-006); (5) the `Safe_UInt__Port` ValueError for None needs investigation — it may be a Type_Safe primitive bug (TASK-001); (6) `export_schemas.py` and `State_Machine__Utils.py` both build Mermaid output with raw string construction — should use MGraph_DB (REFACTOR-007/008).

## DevOps

TASK-006 is the primary CI performance target: wire the server-pooling PoC into `SG_Send__Browser__Test_Harness._start_api_server()` by persisting the PID in `Schema__Harness_State` and reconnecting when the process is still alive. The timing data shows `_start_api_server` costs ~230 ms per test class; if shared across the suite this becomes a one-time cost. TASK-007 and TASK-008 are branch hygiene tasks — review and delete `origin/claude/create-qa-explorer-team-Tg5A6` and `origin/claude/qa-site-v030-integration-Tg5A6`. The CLI (`run_tests.py`) lacks granularity and needs subcommands for per-test execution and http-vs-browser mode selection (REFACTOR-012) before Lambda-triggered runs are practical.

## Librarian

Next harvest cycle should monitor: (a) whether TASK-003/004/005 OSBot-Utils issues are filed and linked back to source files; (b) progress on REFACTOR-001 (harness decomposition) as it will generate significant new files and rename attributes across the codebase; (c) TASK-006 server pooling implementation — once wired, the performance data in section E of the harvest becomes stale and the table should be updated; (d) TASK-007/008 branch deletions — confirm branches are removed after content review; (e) the `QA_Generate_Docs.py` hardcoded `tests_dir` issue (TASK-014 / REFACTOR-013) which will break doc generation when v031 folders are added.

## Sherpa

Two patterns from this session are worth documenting for onboarding: (1) the `# todo: @role` comment-as-communication protocol — how developers leave structured messages for agents, how the harvest process picks them up, and how tracking refs (e.g., `[LIB-2026-04-01-031]`) replace the original comments; (2) the `__()` / `obj()` / `Type_Safe().obj()` assertion pattern used in `test_Page__Send_SGraph_Ai__Upload` — this provides deeply readable structural assertions without custom matchers, and the harvest explicitly asked both Developer and Architect to adopt it as a standard (Example 4 in section B). Both patterns appear in multiple places in the codebase and will recur; new agents should understand them from day one.

---

*Agent briefings — SG/Send QA — harvest 2026-04-01*
