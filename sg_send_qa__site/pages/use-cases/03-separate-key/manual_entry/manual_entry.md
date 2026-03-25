---
title: "Use Case: Manual Entry"
permalink: /pages/use-cases/manual_entry/
---

# Manual Entry

UC-09: Manual token/ID entry form (P1).

Test flow:
  - Navigate to /en-gb/download/ with no hash fragment
  - Verify entry form appears (input + "Decrypt & Download" button)
  - Enter a valid friendly token (from a previous upload)
  - Verify it resolves and decrypts
  - Enter a bogus token → verify error message

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `entry_form_shown_without_hash` | Navigating to /en-gb/download/ with no hash shows the entry form. | 1 |
| `entry_form_has_decrypt_button` | Entry form has a Decrypt & Download (or similar) button. | 1 |
| `bogus_token_shows_error` | Entering a bogus token shows an error (not a crash). | 1 |
| `valid_transfer_id_resolves` | Entering a valid transfer ID resolves and shows the file. | 1 |
| `hash_navigation_to_download` | Navigating directly to /en-gb/download/#id/key auto-decrypts (P1). | 1 |

## Screenshots

### 01 Entry Form

Manual entry form without hash

![01 Entry Form](screenshots/01_entry_form.png)

### 02 Decrypt Button

Entry form with decrypt button

![02 Decrypt Button](screenshots/02_decrypt_button.png)

### 03 Bogus Token Error

Error after bogus token

![03 Bogus Token Error](screenshots/03_bogus_token_error.png)

### 04 Valid Id Resolved

Valid transfer ID resolved

![04 Valid Id Resolved](screenshots/04_valid_id_resolved.png)

### 05 Direct Hash Nav

Direct hash navigation to download

![05 Direct Hash Nav](screenshots/05_direct_hash_nav.png)

