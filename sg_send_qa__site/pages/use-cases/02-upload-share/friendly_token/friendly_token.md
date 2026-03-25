---
title: "Use Case: Friendly Token"
permalink: /pages/use-cases/02-upload-share/friendly_token/
---

# Friendly Token

UC-03: Friendly Token — Simple Token share mode (P0).

This was a P0 bug — critical to test.

Flow:
  1. Upload a file with Simple Token share mode
  2. Capture the friendly token (word-word-NNNN format)
  3. Open a new tab to /en-gb/browse/#<friendly-token>
  4. Verify the token resolves and content decrypts

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `friendly_token_upload_and_resolve` | Upload with Simple Token mode, then resolve the friendly token in a new tab. | 5 |
| `friendly_token_format` | Verify the friendly token matches the word-word-NNNN pattern. | 3 |
| `friendly_token_resolves_in_new_tab` | Upload with Simple Token, then open the token in a new browser tab. | 4 |
| `friendly_token_no_key_in_url_after_decrypt` | After decryption, the friendly token remains in the URL (by design). | 4 |

## Screenshots

### 05 Hash Cleared

URL after decrypt: http://localhost:10062/en-gb/browse/#terra-chain-5022

![05 Hash Cleared](screenshots/05_hash_cleared.png)

### 05 Token Captured

Token: water-climb-1061

![05 Token Captured](screenshots/05_token_captured.png)

### 06 Token Resolved

Token 'water-climb-1061' resolved

![06 Token Resolved](screenshots/06_token_resolved.png)

### 05 Token Resolved

Token 'jungle-valve-4205'

![05 Token Resolved](screenshots/05_token_resolved.png)

### 01 File Selected

File selected (delivery step active)

![01 File Selected](screenshots/01_file_selected.png)

### 02 Simple Token Selected

Simple Token selected

![02 Simple Token Selected](screenshots/02_simple_token_selected.png)

### 03 Upload Complete

Upload complete

![03 Upload Complete](screenshots/03_upload_complete.png)

### 05 Hash After Decrypt

URL after decrypt: http://localhost:10062/en-gb/browse/#umber-ocean-2218

![05 Hash After Decrypt](screenshots/05_hash_after_decrypt.png)

