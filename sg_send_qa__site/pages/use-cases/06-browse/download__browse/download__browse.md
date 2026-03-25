---
title: "Use Case: Download  Browse"
permalink: /pages/use-cases/06-browse/download__browse/
---

# Download  Browse

UC-07: Browse view features (P1).

Test flow:
  - Verify folder tree renders with expand/collapse controls
  - Verify file click opens preview tab in right panel
  - Verify keyboard navigation: j/k moves through files, s saves
  - Verify Share tab shows URL + copy + email
  - Verify Info tab shows file counts by type, encryption info
  - Verify "Save locally" downloads the zip
  - Verify print button is present

---

## Test Methods

| Method | Description | Screenshots |
|--------|-------------|:-----------:|
| `browse_page_loads` | Browse page loads without errors. | 1 |
| `folder_tree_present` | Folder tree is rendered in the left panel. | 1 |
| `file_click_opens_preview` | Clicking a file in the tree opens a preview in the right panel. | 0 |
| `share_tab_present` | Share tab shows URL, copy, and email actions. | 0 |
| `info_tab_present` | Info tab shows file counts and encryption info. | 0 |
| `save_locally_button_present` | Save locally button is present in browse view. | 1 |
| `keyboard_navigation_j_k` | Keyboard j/k navigate through files in browse view (P2). | 2 |

## Screenshots

### 01 Browse Loaded

Browse view loaded

![01 Browse Loaded](screenshots/01_browse_loaded.png)

### 02 Folder Tree

Folder tree in browse view

![02 Folder Tree](screenshots/02_folder_tree.png)

### 06 Save Button

Save locally button

![06 Save Button](screenshots/06_save_button.png)

### 07 Keyboard J

After pressing j

![07 Keyboard J](screenshots/07_keyboard_j.png)

### 08 Keyboard K

After pressing k

![08 Keyboard K](screenshots/08_keyboard_k.png)

