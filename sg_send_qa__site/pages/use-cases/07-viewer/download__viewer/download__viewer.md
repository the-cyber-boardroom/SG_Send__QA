---
title: "Use Case: Download  Viewer"
permalink: /pages/use-cases/07-viewer/download__viewer/
---

# Download  Viewer

UC-08: Single file viewer (P1).

Test flow:
  - Upload a markdown file via API, open the download/view link
  - Verify markdown renders (or content displays)
  - Verify Share button toggles share panel with download link
  - Verify Copy copies the URL with key intact
  - Verify Print button is present
  - Verify Save locally downloads the file

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `viewer_page_loads` | Single-file viewer loads without errors. | 1 |
| `markdown_content_displayed` | Markdown file content is decrypted and displayed. | 1 |
| `share_button_present` | Share button is present and toggles the share panel. | 2 |
| `copy_url_contains_key` | The share URL shown in the panel contains the key (hash fragment). | 1 |
| `save_locally_button_present` | Save locally button is present in the viewer. | 1 |
| `short_url_v_route` | Short URL /en-gb/v/ works the same as /en-gb/view/. | 1 |

## Screenshots

### 01 Viewer Loaded

Single file viewer loaded

![01 Viewer Loaded](screenshots/01_viewer_loaded.png)

### 02 Content

Decrypted markdown content

![02 Content](screenshots/02_content.png)

### 03 Before Share

Before share panel

![03 Before Share](screenshots/03_before_share.png)

### 04 Share Panel

Share panel opened

![04 Share Panel](screenshots/04_share_panel.png)

### 05 Url With Key

URL input with key

![05 Url With Key](screenshots/05_url_with_key.png)

### 06 Save Button

Save locally button

![06 Save Button](screenshots/06_save_button.png)

### 07 Short Url V

Short /v/ route loads viewer

![07 Short Url V](screenshots/07_short_url_v.png)

