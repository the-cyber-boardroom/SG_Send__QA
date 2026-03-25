---
title: "Use Case: Separate Key"
permalink: /pages/use-cases/03-separate-key/separate_key/
---

# Separate Key

UC-05: Separate Key share mode (P0).

Flow:
  1. Upload a file with Separate Key share mode
  2. Get a link (no key in hash) and the key separately
  3. Open the link → verify "ready" state with key input
  4. Paste the key, click Decrypt
  5. Verify content displays
  6. Try a wrong key → verify error message

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `separate_key_decrypt_via_api` | Create a transfer via API, open link without key, enter key manually. | 4 |
| `wrong_key_shows_error` | Enter an incorrect key and verify an error message appears. | 1 |
| `separate_key_ui_flow` | Full UI flow: upload with Separate Key mode, extract link + key, verify. | 2 |

## Screenshots

### 01 Ready State

Download page — ready state, key input visible

![01 Ready State](screenshots/01_ready_state.png)

### 02 Transfer Info

Transfer info displayed before key entry

![02 Transfer Info](screenshots/02_transfer_info.png)

### 03 Key Entered

Encryption key entered

![03 Key Entered](screenshots/03_key_entered.png)

### 04 Decrypted

Content decrypted with separate key

![04 Decrypted](screenshots/04_decrypted.png)

### 05 Wrong Key Error

Error message after wrong key

![05 Wrong Key Error](screenshots/05_wrong_key_error.png)

### 06 Separate Key Selected

Separate Key mode selected

![06 Separate Key Selected](screenshots/06_separate_key_selected.png)

### 07 Separate Key Done

Upload complete — link and key shown separately

![07 Separate Key Done](screenshots/07_separate_key_done.png)

