---
title: "Use Case: Upload  Single File"
permalink: /pages/use-cases/upload__single_file/
---

# Upload  Single File

UC-01: Single file upload → download → content matches (P0).

Happy-path end-to-end test:
  1. Navigate to the upload page
  2. Drop a text file onto the upload zone
  3. Walk through the 6-step wizard
  4. Capture the download link
  5. Open the download link in a new page
  6. Verify decrypted content matches the original

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `upload_page_loads` | Navigate to /en-gb/ and verify the upload zone is visible. | 1 |
| `single_file_upload_flow` | Upload a text file through the wizard and verify the download link works. | 6 |
| `download_link_format` | Verify the download link contains transfer ID and key in the hash. | 5 |
| `footer_version` | Verify the footer shows v0.3.0. | 1 |

## Screenshots

### 01 Upload Page

Upload page loaded

![01 Upload Page](screenshots/01_upload_page.png)

### 05 Download Page

Download page — awaiting decrypt

![05 Download Page](screenshots/05_download_page.png)

### 06 Decrypted

Content decrypted and visible

![06 Decrypted](screenshots/06_decrypted.png)

### 01 File Selected

File selected — delivery step

![01 File Selected](screenshots/01_file_selected.png)

### 02 Share Step

Share mode step

![02 Share Step](screenshots/02_share_step.png)

### 03 Mode Selected

Combined link selected

![03 Mode Selected](screenshots/03_mode_selected.png)

### 04 Upload Done

Upload complete — link shown

![04 Upload Done](screenshots/04_upload_done.png)

### 07 Link Format

Link verified: http://localhost:10062/en-gb/browse/#c419e004d960/C7GKS6VAOu4HsoRQ9tGEdTKpnP6pi9

![07 Link Format](screenshots/07_link_format.png)

### 01 Footer

Footer showing version

![01 Footer](screenshots/01_footer.png)

