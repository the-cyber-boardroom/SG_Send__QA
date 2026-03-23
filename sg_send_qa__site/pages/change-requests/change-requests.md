---
title: Change Requests to Send UI Team
permalink: /pages/change-requests/
---

# Change Requests to Send UI Team

Requests from the **QA Agentic Team** to the **Send UI Agentic Team** for changes that would make automated tests more resilient, performant, and stable.

Each request includes the problem we hit during testing, the current workaround in our test code, and the proposed fix in the SG/Send UI.

---

## Status Key

| Status | Meaning |
|--------|---------|
| **Open** | Awaiting UI team action |
| **Accepted** | UI team has acknowledged and planned the change |
| **Shipped** | Change deployed — QA team can remove workaround |
| **Won't Fix** | UI team declined — workaround becomes permanent |

---

## CR-001: `networkidle` never resolves due to background API calls

| Field | Value |
|-------|-------|
| **Status** | Open |
| **Priority** | High |
| **Affected tests** | All browser tests |
| **Workaround** | `browser_helpers.goto()` uses `domcontentloaded` instead of `networkidle` |

**Problem:** The SG/Send UI makes continuous background API calls (health checks, token validation polling) that prevent Playwright's `networkidle` wait strategy from ever resolving. Every `page.goto()` with the default wait strategy times out after 30 seconds.

**Impact:** Tests that use `networkidle` (the Playwright recommended default) fail with timeouts. We had to build a custom `goto()` helper that uses `domcontentloaded`, but this means we can't be certain the page is fully interactive when we start asserting.

**Proposed fix:** Either:
1. Defer background polling until after initial render is complete, or
2. Use a visible DOM signal (e.g., a `data-ready` attribute on `<body>`) that tests can wait for, indicating the UI is fully initialised

**QA file reference:** `tests/qa/v030/browser_helpers.py:4-11`

---

## CR-002: Access gate button order causes mis-clicks

| Field | Value |
|-------|-------|
| **Status** | Open |
| **Priority** | Medium |
| **Affected tests** | All access gate tests (UC-10) |
| **Workaround** | Target `#access-token-submit` by ID instead of generic button selector |

**Problem:** The access gate renders buttons in this order:
1. `#toggle-token-vis` — eye icon (show/hide password)
2. `#access-token-submit` — the "Go" button

A generic `page.locator("button").first` selector hits the eye icon, not the Go button. Additionally, the language dropdown button in the top nav is also a `<button>`, so clicking "first button on page" opens the language selector instead.

**Impact:** Screenshot `02_after_token` was captured with the language dropdown open, obscuring the page content. Tests that relied on generic button selectors were clicking the wrong element entirely.

**Proposed fix:**
1. Add `data-testid="access-gate-submit"` to the Go button
2. Add `data-testid="access-gate-input"` to the token input
3. Consider adding `data-testid` attributes to all interactive elements as a general practice — this is the standard approach for test-friendly UIs

**QA file reference:** `tests/qa/v030/browser_helpers.py:14-28`

---

## CR-003: Add `data-testid` attributes to key UI elements

| Field | Value |
|-------|-------|
| **Status** | Open |
| **Priority** | High |
| **Affected tests** | All browser tests |
| **Workaround** | We use element IDs (`#access-token-input`, `#access-token-submit`) where available, fall back to fragile CSS/text selectors elsewhere |

**Problem:** Most UI elements lack stable test identifiers. Tests currently rely on a mix of:
- Element IDs (only available on the access gate)
- CSS selectors (`input[type='file']`)
- Text content matching (`button:has-text('Go')`)
- Generic position selectors (`page.locator("button").first`)

These selectors break when the UI is restructured, reworded, or reordered — even if the functionality hasn't changed.

**Impact:** Test maintenance burden increases with every UI change. Selectors that work today may silently target the wrong element tomorrow (as CR-002 demonstrated).

**Proposed fix:** Add `data-testid` attributes to all key interactive elements:

```html
<!-- Access gate -->
<input data-testid="access-gate-input" ... />
<button data-testid="access-gate-submit">Go</button>
<button data-testid="access-gate-toggle-visibility">...</button>

<!-- File sharing -->
<input data-testid="file-upload-input" type="file" ... />
<div data-testid="upload-zone">...</div>
<div data-testid="file-list">...</div>

<!-- Navigation -->
<button data-testid="language-selector">EN-GB</button>
<nav data-testid="main-nav">...</nav>
```

`data-testid` attributes are invisible to users, have no styling impact, and provide a contract between the UI and test automation that survives refactoring.

---

## CR-004: Token counter behaviour undocumented

| Field | Value |
|-------|-------|
| **Status** | Open |
| **Priority** | Low |
| **Affected tests** | `tests/qa/v030/via__httpx/test__access_gate.py` |
| **Workaround** | Test documents observed behaviour but can't assert expected behaviour |

**Problem:** The access token appears to have a usage counter, but the behaviour when the counter reaches zero is not documented. Should the token be denied? Should it still work? Is there a grace period?

**Impact:** We can't write definitive pass/fail assertions for token exhaustion scenarios because the expected behaviour is undefined.

**Proposed fix:** Document the token counter lifecycle:
- What happens when counter reaches zero?
- Is there an API endpoint to check remaining uses?
- Does the UI show remaining uses to the user?

---

## Summary

| CR | Title | Priority | Status |
|:--:|-------|:--------:|:------:|
| 001 | `networkidle` never resolves | High | Open |
| 002 | Access gate button order | Medium | Open |
| 003 | Add `data-testid` attributes | High | Open |
| 004 | Token counter undocumented | Low | Open |

---

*This page is maintained by the QA Agentic Team. To discuss a change request, comment on the relevant issue or reach out via the team channel.*
