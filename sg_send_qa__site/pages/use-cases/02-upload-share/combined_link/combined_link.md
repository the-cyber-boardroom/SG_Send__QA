---
title: "Use Case: Combined Link"
permalink: /pages/use-cases/02-upload-share/combined_link/
---

# Combined Link

UC-04: Combined Link share mode (P0).

Flow:
  1. Upload a file with Combined Link share mode
  2. Capture the full link (contains #transferId/base64key)
  3. Open the link in a new tab
  4. Verify auto-decrypt and content display

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `combined_link_upload_and_auto_decrypt` | Upload with Combined Link, open the link, verify auto-decryption. | 6 |
| `combined_link_via_api_helper` | Create an encrypted transfer via API helper, then open the combined link in browser. | 1 |

## Screenshots

### 01 File Selected

File selected (delivery step active)

![01 File Selected](screenshots/01_file_selected.png)

### 02 Share Step

Share mode step

![02 Share Step](screenshots/02_share_step.png)

### 03 Mode Selected

Combined link selected

![03 Mode Selected](screenshots/03_mode_selected.png)

### 04 Upload Complete

Upload complete

![04 Upload Complete](screenshots/04_upload_complete.png)

### 06 Link Captured

Combined link: http://localhost:10062/en-gb/browse/#88ab11d1b122/GghtrwypXeZTn9ljHpZuK0g4N0rsyp

![06 Link Captured](screenshots/06_link_captured.png)

### 07 Auto Decrypted

Auto-decrypted content

![07 Auto Decrypted](screenshots/07_auto_decrypted.png)

### 01 Api Created Decrypt

Decrypted content from API-created transfer

![01 Api Created Decrypt](screenshots/01_api_created_decrypt.png)

