# Reference: Team Structure & Decisions

**Maintained by:** Librarian
**Last updated:** 2026-03-23

---

## Team Roles

| Role | File | Mission |
|------|------|---------|
| **QA Lead** | [`team/roles/qa-lead/ROLE.md`](../qa-lead/ROLE.md) | Test strategy, quality gates, coverage priorities, bug documentation |
| **Developer** | [`team/roles/dev/ROLE.md`](../dev/ROLE.md) | Test implementation, Playwright code, server, CLI, doc generator |
| **Architect** | [`team/roles/architect/ROLE.md`](../architect/ROLE.md) | System design, tool decisions, API contracts |
| **DevOps** | [`team/roles/devops/ROLE.md`](../devops/ROLE.md) | CI/CD pipelines, GitHub Actions, deployment, Lambda |
| **Librarian** | [`team/roles/librarian/ROLE.md`](../librarian/ROLE.md) | Knowledge management, indexing, cross-references |
| **Sherpa** | [`team/roles/sherpa/ROLE.md`](../sherpa/ROLE.md) | Onboarding, best practices, troubleshooting |

---

## Role Interactions

```
QA Lead ←──── test specs ────→ Developer
   │                              │
   │ quality gates                │ CI issues
   │                              │
   ▼                              ▼
Architect                     DevOps
   │                              │
   │ tool decisions               │ deployment
   │                              │
   ▼                              ▼
Librarian ←── doc structure ──→ Sherpa
   │                              │
   │ indexing                      │ readability
   └──────── knowledge ───────────┘
```

---

## Human Team Members

### Dinis Cruz (Project Owner)

**Location:** `team/humans/dinis_cruz/`

#### Briefs (task assignments)

| Date | File | Topic |
|------|------|-------|
| 2026-03-22 | `briefs/03/22/v0.1.0__brief__local-api-server-for-SG_Send__QA.md` | Local API server setup |
| 2026-03-22 | `briefs/03/22/v0.16.45__qa-brief__v030-acceptance-tests.md` | v0.3.0 acceptance test suite |

#### Debriefs (session reviews)

| Date | File | Topic |
|------|------|-------|
| 2026-02-23 | `debriefs/02/23/23__refactoring-review-and-ci-milestone.md` | File refactoring review + CI milestone (27 stale path references found) |
| 2026-03-22 | `debriefs/03/22/v0.2.10__browser-tests-briefing.md` | Browser tests briefing |
| 2026-03-22 | `debriefs/03/22/v0.2.10__playwright-setup-guide.md` | Playwright setup guide |

---

## Knowledge Records

Significant milestones documented by the Librarian.

| Date | Version | File | Milestone |
|------|---------|------|-----------|
| 2026-02-23 | v0.2.2 | `knowledge/2026-02-23__ci-pipeline-green-and-docs-live.md` | CI pipeline green on all 4 jobs, custom domain live at qa.send.sgraph.ai |

---

## Key Decisions (from debriefs and role files)

| Decision | Made by | Rationale | Reference |
|----------|---------|-----------|-----------|
| Playwright over Selenium | Architect | Native Python, pytest integration, auto-waiting, CDP screenshots | `team/roles/architect/ROLE.md` |
| No mocks, ever | QA Lead | Tests must exercise real behaviour; mocks hide bugs | `team/roles/qa-lead/ROLE.md` |
| Content bundle pattern | Architect | Self-contained use-case dirs scale cleanly for static sites | Refactoring debrief |
| `sg_send_qa__site/` naming | Architect | Follows OSBot/CB double-underscore convention | Refactoring debrief |
| SG/Send dev branch only | Explorer | PyPI package is behind; dev branch has latest API/UI | `.claude/explorer/CLAUDE.md` |
| `localhost` not `127.0.0.1` | Developer | Web Crypto API needs secure context; `localhost` qualifies | `tests/qa/v030/conftest.py` |
| No `__init__.py` in test dirs | QA Lead | Breaks PyCharm test discovery; pytest doesn't need them | `.claude/CLAUDE.md` |
| Bug test pattern (dual tests) | QA Lead + Dev | Normal test asserts expected; bug test asserts buggy → evidence | `team/roles/dev/ROLE.md` |

---

## Agent Guidance Files

| File | Purpose | Who reads it |
|------|---------|-------------|
| `.claude/CLAUDE.md` | Project-wide rules, stack, key rules, role table | Every agent on session start |
| `.claude/explorer/CLAUDE.md` | Explorer team mission, composition, priorities | Explorer team agents |
| `team/roles/*/ROLE.md` | Role-specific rules, patterns, workflows | Agent assigned to that role |

**Session start protocol** (from CLAUDE.md):
1. Read `.claude/CLAUDE.md` for project-wide rules
2. Read your role's `ROLE.md` for operational detail
3. Check current state of your area (tests, docs, CI, etc.)

---

*SG/Send QA — Team Structure Reference — Librarian Reference*
