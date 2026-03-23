---
title: Known Bugs
permalink: /pages/use-cases/bugs/
---

# Known Bugs

Bugs discovered by automated tests, documented with screenshots. Each bug has a test that **passes while the bug exists** — when the bug is fixed, the test fails and can be removed.

---

## BUG-001: Generic button selector opens language dropdown

| Field | Value |
|-------|-------|
| **Related CR** | [CR-002](/pages/change-requests/#cr-002-access-gate-button-order-causes-mis-clicks) |
| **Test file** | `tests/qa/v030/bugs/test__bug__generic_button_opens_language_dropdown.py` |
| **Affected** | Access gate (UC-10) |

The first `<button>` element on the page is the language selector (EN-GB), not the access gate's Go button. Clicking `page.locator("button").first` opens the language dropdown, obscuring the page.

**Workaround:** Target `#access-token-submit` by ID.

{% if site.screenshots.bug__language_dropdown_opened %}
![Language dropdown opened by mistake](screenshots/bug__language_dropdown_opened.png)
{% endif %}

---

## How Bug Tests Work

```
tests/qa/v030/
├── test__access_gate.py          ← asserts CORRECT behaviour (fails on bug)
└── bugs/
    └── test__bug__*.py           ← asserts BUGGY behaviour (passes on bug)
```

| State | Normal test | Bug test | Action |
|-------|:-----------:|:--------:|--------|
| Bug exists | FAIL | PASS | Bug is documented with screenshots |
| Bug fixed | PASS | FAIL | Remove the bug test |
