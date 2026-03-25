---
title: "Use Case: Access Gate Standalone"
permalink: /pages/use-cases/01-access-gate/access_gate_standalone/
---

# Access Gate Standalone

Standalone access gate test: UC-10 (P1).

Merged from tests/standalone/ into v030 as part of Phase 2 refactoring.
Uses the shared v030 fixtures (QA server, UI server, screenshots).

Screenshots are saved to:
    sg_send_qa__site/pages/use-cases/access_gate_standalone/screenshots/

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `upload_accessible_with_token` | Providing the correct access token grants access to the upload zone. | 1 |
| `wrong_token_shows_error` | Providing a wrong access token shows an error. | 0 |
| `upload_zone_visible_without_gate` | If no gate is configured, upload zone is immediately visible. | 1 |

## Screenshots

### 01 Landing

Landing page (may show gate or upload zone)

![01 Landing](screenshots/01_landing.png)

### 04 No Gate

Upload zone without gate

![04 No Gate](screenshots/04_no_gate.png)

