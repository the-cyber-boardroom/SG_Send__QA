---
title: "Use Case: Upload  Folder"
permalink: /pages/use-cases/upload__folder/
---

# Upload  Folder

UC-02: Folder upload → gallery + browse view (P1).

Test flow:
  1. Upload a folder containing 3+ images and a markdown file
  2. Verify gallery mode is auto-selected (3+ images triggers gallery)
  3. Verify thumbnail grid renders with correct file count
  4. Click a thumbnail → verify lightbox opens
  5. Close lightbox → click "Folder view" link
  6. Verify browse view loads with folder tree
  7. Click a file in the tree → verify it opens in preview
  8. Click "Gallery view" → verify it switches back

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `upload_zip_and_gallery_view` | Upload a zip with 3+ images; verify gallery mode is shown. | 5 |
| `gallery_thumbnail_grid` | Create a zip upload via API, open gallery, verify thumbnail grid. | 1 |
| `browse_view_folder_tree` | Open browse view for the zip; verify folder tree is present. | 1 |
| `mode_switch_preserves_hash` | Gallery ↔ browse mode switching preserves the hash fragment. | 1 |

## Screenshots

### 01 Upload Page

Upload page loaded

![01 Upload Page](screenshots/01_upload_page.png)

### 02 File Selected

Zip file selected — delivery step

![02 File Selected](screenshots/02_file_selected.png)

### 03 Share Step

Share mode step

![03 Share Step](screenshots/03_share_step.png)

### 04 Upload Done

Upload complete — link shown

![04 Upload Done](screenshots/04_upload_done.png)

### 05 Download Gallery

Gallery view after zip download

![05 Download Gallery](screenshots/05_download_gallery.png)

### 06 Gallery Thumbnails

Gallery thumbnail grid

![06 Gallery Thumbnails](screenshots/06_gallery_thumbnails.png)

### 07 Browse View

Browse view with folder tree

![07 Browse View](screenshots/07_browse_view.png)

### 08 Switched To Browse

Switched to browse view

![08 Switched To Browse](screenshots/08_switched_to_browse.png)

